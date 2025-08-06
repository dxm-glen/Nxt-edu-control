#!/usr/bin/env python3
"""
CloudFormation 템플릿 생성기
환경변수를 사용하여 동적으로 IAM 사용자 생성 템플릿을 생성합니다.
"""

import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()


def get_policy_arns():
    """환경변수에서 정책 ARN 목록을 가져옵니다."""
    # AWS 계정 ID를 환경변수에서 가져오기
    aws_account_id = os.getenv("AWS_ACCOUNT_ID", "YOUR_ACCOUNT_ID")

    policy_arns = [
        os.getenv(
            "POLICY_ARN_ALLOW_NON_OVERKILL",
            f"arn:aws:iam::{aws_account_id}:policy/AllowNonOverkill",
        ),
        os.getenv(
            "POLICY_ARN_IAM_BASIC_ACCESS",
            f"arn:aws:iam::{aws_account_id}:policy/IAMBasicAccess",
        ),
        os.getenv(
            "POLICY_ARN_SAFE_POWER_USER",
            f"arn:aws:iam::{aws_account_id}:policy/SafePowerUser",
        ),
        os.getenv(
            "POLICY_ARN_CONTROL_OWN_RESOURCES",
            f"arn:aws:iam::{aws_account_id}:policy/ControlOnlyOwnResources",
        ),
        os.getenv(
            "POLICY_ARN_RESTRICT_REGION_VIRGINIA",
            f"arn:aws:iam::{aws_account_id}:policy/RestrictRegionVirginia",
        ),
    ]
    return policy_arns


def generate_policy_array_string(policy_arns):
    """Python 리스트 형식으로 정책 ARN 문자열 생성"""
    formatted_arns = [f'                          "{arn}"' for arn in policy_arns]
    return ",\n".join(formatted_arns)


def generate_template():
    """환경변수를 사용하여 CloudFormation 템플릿 생성"""

    # 환경변수에서 값 가져오기
    policy_arns = get_policy_arns()
    default_password = os.getenv("DEFAULT_USER_PASSWORD")

    # Lambda 함수용 정책 ARN 배열 생성
    create_policy_array = generate_policy_array_string(policy_arns)
    delete_policy_array = generate_policy_array_string(policy_arns)

    template_content = f"""AWSTemplateFormatVersion: "2010-09-09"
Description: "지정된 그룹과 정책으로 다수의 IAM 사용자를 생성하는 CloudFormation 템플릿"

Parameters:
  GroupName:
    Type: String
    Description: "IAM 그룹명 (예: groupname)"
    Default: "groupname"
    MinLength: 1
    MaxLength: 64
    AllowedPattern: "^[a-zA-Z0-9+=,.@_-]+$"

  UserCount:
    Type: Number
    Description: "생성할 최대 사용자 번호 (예: 30 입력시 00부터 30까지 총 31명 생성)"
    Default: 30
    MinValue: 1
    MaxValue: 100

Resources:
  # IAM Group
  IAMGroup:
    Type: AWS::IAM::Group
    Properties:
      GroupName: !Ref GroupName
      Path: "/"

  # Lambda function to create multiple users
  UserCreatorFunction:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: !Sub "${{AWS::StackName}}-UserCreator"
      Runtime: python3.9
      Handler: index.lambda_handler
      Role: !GetAtt UserCreatorRole.Arn
      Timeout: 900
      Code:
        ZipFile: |
          import boto3
          import cfnresponse
          import json
          import string
          import time

          def lambda_handler(event, context):
              print(f"이벤트 수신: {{json.dumps(event)}}")
              
              try:
                  iam = boto3.client('iam')
                  
                  if event['RequestType'] == 'Create':
                      group_name = event['ResourceProperties']['GroupName']
                      user_count = int(event['ResourceProperties']['UserCount'])
                      
                      print(f"그룹 '{{group_name}}'에 {{user_count + 1}}명의 사용자 생성 시작")
                      
                      # Fixed policy ARNs
                      policy_arns = [
{create_policy_array}
                      ]
                      
                      # Create users
                      created_users = []
                      failed_users = []
                      
                      for i in range(user_count + 1):  # 00 to user_count
                          user_name = f"{{group_name}}-{{i:02d}}"
                          
                          try:
                              # Create user
                              print(f"사용자 생성 중: {{user_name}}")
                              iam.create_user(UserName=user_name, Path='/')
                              
                              # Set initial password
                              print(f"사용자 '{{user_name}}' 초기 비밀번호 설정 중")
                              iam.create_login_profile(
                                  UserName=user_name,
                                  Password='{default_password}',
                                  PasswordResetRequired=True
                              )
                              
                              # Add user to group
                              print(f"사용자 '{{user_name}}'을 그룹 '{{group_name}}'에 추가 중")
                              iam.add_user_to_group(
                                  GroupName=group_name,
                                  UserName=user_name
                              )
                              
                              created_users.append(user_name)
                              print(f"사용자 '{{user_name}}' 생성 완료")
                              
                          except Exception as user_error:
                              print(f"사용자 '{{user_name}}' 생성 실패: {{str(user_error)}}")
                              failed_users.append(f"{{user_name}}: {{str(user_error)}}")
                              # Continue with other users instead of failing completely
                      
                      # Attach multiple policies to group
                      attached_policies = []
                      failed_policies = []
                      
                      for policy_arn in policy_arns:
                          try:
                              print(f"정책 연결 중: {{policy_arn}}")
                              iam.attach_group_policy(
                                  GroupName=group_name,
                                  PolicyArn=policy_arn
                              )
                              attached_policies.append(policy_arn)
                              print(f"정책 연결 완료: {{policy_arn}}")
                          except Exception as policy_error:
                              print(f"정책 연결 실패 '{{policy_arn}}': {{str(policy_error)}}")
                              failed_policies.append(f"{{policy_arn}}: {{str(policy_error)}}")
                      
                      # Simplified response data to avoid size issues
                      response_data = {{
                          'UserCount': len(created_users),
                          'PolicyCount': len(attached_policies),
                          'Status': 'Success'
                      }}
                      
                      print(f"작업 완료. 생성된 사용자: {{len(created_users)}}명, 연결된 정책: {{len(attached_policies)}}개")
                      if failed_users:
                          print(f"생성 실패한 사용자: {{failed_users}}")
                      if failed_policies:
                          print(f"연결 실패한 정책: {{failed_policies}}")
                      
                      # Consider it successful if at least some users were created
                      if len(created_users) > 0:
                          cfnresponse.send(event, context, cfnresponse.SUCCESS, response_data)
                      else:
                          cfnresponse.send(event, context, cfnresponse.FAILED, response_data)
                      
                  elif event['RequestType'] == 'Delete':
                      group_name = event['ResourceProperties']['GroupName']
                      user_count = int(event['ResourceProperties']['UserCount'])
                      
                      print(f"그룹 '{{group_name}}'에서 {{user_count + 1}}명의 사용자 삭제 시작")
                      
                      # Fixed policy ARNs
                      policy_arns = [
{delete_policy_array}
                      ]
                      
                      deleted_users = []
                      failed_deletions = []
                      
                      # Delete users with retry logic
                      for i in range(user_count + 1):
                          user_name = f"{{group_name}}-{{i:02d}}"
                          
                          # Try to delete user with retries for EntityTemporarilyUnmodifiable
                          max_retries = 5
                          retry_delay = 10  # seconds
                          
                          for attempt in range(max_retries):
                              try:
                                  print(f"사용자 삭제 중: {{user_name}} (시도 {{attempt + 1}}/{{max_retries}})")
                                  
                                  # Remove user from group
                                  try:
                                      iam.remove_user_from_group(
                                          GroupName=group_name,
                                          UserName=user_name
                                      )
                                  except Exception as e:
                                      print(f"경고: 사용자 '{{user_name}}'을 그룹에서 제거 실패: {{e}}")
                                  
                                  # Delete login profile with retry
                                  login_profile_deleted = False
                                  for lp_attempt in range(3):
                                      try:
                                          iam.delete_login_profile(UserName=user_name)
                                          login_profile_deleted = True
                                          print(f"사용자 '{{user_name}}' 로그인 프로필 삭제 완료")
                                          break
                                      except Exception as lp_e:
                                          if "EntityTemporarilyUnmodifiable" in str(lp_e) and lp_attempt < 2:
                                              print(f"사용자 '{{user_name}}' 로그인 프로필이 일시적으로 수정 불가능, {{retry_delay}}초 대기 중...")
                                              time.sleep(retry_delay)
                                          else:
                                              print(f"사용자 '{{user_name}}' 로그인 프로필 삭제 실패: {{lp_e}}")
                                              break
                                  
                                  # Delete user
                                  iam.delete_user(UserName=user_name)
                                  deleted_users.append(user_name)
                                  print(f"사용자 '{{user_name}}' 삭제 완료")
                                  break  # Success, exit retry loop
                                  
                              except Exception as e:
                                  error_msg = str(e)
                                  if "EntityTemporarilyUnmodifiable" in error_msg or "DeleteConflict" in error_msg:
                                      if attempt < max_retries - 1:
                                          print(f"사용자 '{{user_name}}'이 일시적으로 수정 불가능, {{retry_delay}}초 대기 후 재시도 {{attempt + 2}}")
                                          time.sleep(retry_delay)
                                          continue
                                  
                                  print(f"사용자 '{{user_name}}' 삭제 오류: {{error_msg}}")
                                  failed_deletions.append(f"{{user_name}}: {{error_msg}}")
                                  break  # Give up on this user
                      
                      # Detach policies from group
                      detached_policies = []
                      failed_detachments = []
                      
                      for policy_arn in policy_arns:
                          try:
                              print(f"정책 분리 중: {{policy_arn}}")
                              iam.detach_group_policy(
                                  GroupName=group_name,
                                  PolicyArn=policy_arn
                              )
                              detached_policies.append(policy_arn)
                              print(f"정책 분리 완료: {{policy_arn}}")
                          except Exception as e:
                              print(f"정책 분리 실패 '{{policy_arn}}': {{str(e)}}")
                              failed_detachments.append(f"{{policy_arn}}: {{str(e)}}")
                      
                      response_data = {{
                          'DeletedCount': len(deleted_users),
                          'DetachedCount': len(detached_policies),
                          'Status': 'Deleted'
                      }}
                      
                      print(f"삭제 작업 완료. 삭제된 사용자: {{len(deleted_users)}}명, 분리된 정책: {{len(detached_policies)}}개")
                      if failed_deletions:
                          print(f"삭제 실패한 사용자: {{failed_deletions}}")
                      if failed_detachments:
                          print(f"분리 실패한 정책: {{failed_detachments}}")
                      
                      cfnresponse.send(event, context, cfnresponse.SUCCESS, response_data)
                  
                  else:
                      cfnresponse.send(event, context, cfnresponse.SUCCESS, {{}})
                      
              except Exception as e:
                  error_msg = str(e)
                  print(f"Lambda 함수 오류: {{error_msg}}")
                  
                  response_data = {{
                      'Status': 'Failed',
                      'Error': error_msg[:200]  # Truncate long error messages
                  }}
                  
                  cfnresponse.send(event, context, cfnresponse.FAILED, response_data)

  # IAM Role for Lambda function
  UserCreatorRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              Service: lambda.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
      Policies:
        - PolicyName: IAMUserManagement
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: Allow
                Action:
                  - iam:CreateUser
                  - iam:DeleteUser
                  - iam:CreateLoginProfile
                  - iam:DeleteLoginProfile
                  - iam:UpdateLoginProfile
                  - iam:AddUserToGroup
                  - iam:RemoveUserFromGroup
                  - iam:AttachGroupPolicy
                  - iam:DetachGroupPolicy
                  - iam:ListUsers
                  - iam:GetUser
                  - iam:ListGroupsForUser
                  - iam:GetGroup
                  - iam:ListAttachedGroupPolicies
                  - iam:TagUser
                  - iam:UntagUser
                  - logs:CreateLogGroup
                  - logs:CreateLogStream
                  - logs:PutLogEvents
                Resource: "*"

  # Custom resource to trigger user creation
  CreateUsers:
    Type: AWS::CloudFormation::CustomResource
    Properties:
      ServiceToken: !GetAtt UserCreatorFunction.Arn
      GroupName: !Ref GroupName
      UserCount: !Sub "${{UserCount}}"
    DependsOn:
      - IAMGroup
      - UserCreatorFunction

Outputs:
  GroupName:
    Description: "생성된 IAM 그룹명"
    Value: !Ref IAMGroup
    Export:
      Name: !Sub "${{AWS::StackName}}-GroupName"

  GroupArn:
    Description: "생성된 IAM 그룹의 ARN"
    Value: !GetAtt IAMGroup.Arn
    Export:
      Name: !Sub "${{AWS::StackName}}-GroupArn"

  UserCountParameter:
    Description: "UserCount 파라미터 값 (실제 생성된 사용자 수 = 이 값 + 1)"
    Value: !Ref UserCount
    Export:
      Name: !Sub "${{AWS::StackName}}-UserCountParameter"

  UserNamingPattern:
    Description: "생성된 사용자명 패턴"
    Value: !Sub "${{GroupName}}-00부터 ${{GroupName}}-${{UserCount}}까지"
    Export:
      Name: !Sub "${{AWS::StackName}}-UserNamingPattern"
"""

    return template_content


def save_template(template_content, output_file="nxtcloud-iamuser-template.yaml"):
    """생성된 템플릿을 파일로 저장"""
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(template_content)
    print(f"✅ CloudFormation 템플릿이 생성되었습니다: {output_file}")


def main():
    """메인 함수"""
    try:
        # 환경변수 확인
        required_vars = ["POLICY_ARN_ALLOW_NON_OVERKILL", "DEFAULT_USER_PASSWORD"]
        missing_vars = [var for var in required_vars if not os.getenv(var)]

        if missing_vars:
            print(f"⚠️ 일부 환경변수가 설정되지 않았습니다: {', '.join(missing_vars)}")
            print("   기본값을 사용합니다.")

        # 템플릿 생성
        template_content = generate_template()

        # 템플릿 파일 저장
        save_template(template_content)

        print("\n📋 사용된 환경변수:")
        print(
            f"- DEFAULT_USER_PASSWORD: {os.getenv('DEFAULT_USER_PASSWORD', '기본값 사용')}"
        )
        print(
            f"- POLICY_ARN_ALLOW_NON_OVERKILL: {os.getenv('POLICY_ARN_ALLOW_NON_OVERKILL', '기본값 사용')}"
        )
        print("- 기타 정책 ARN들...")

        return True

    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return False


if __name__ == "__main__":
    main()
