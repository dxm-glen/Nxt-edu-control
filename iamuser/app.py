import streamlit as st
import subprocess
import os
import json
from datetime import datetime
import pytz
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 페이지 설정
st.set_page_config(
    page_title="NXTCloud IAM 사용자 생성기",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 환경변수에서 설정값 로드
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
DEFAULT_USER_PASSWORD = os.getenv("DEFAULT_USER_PASSWORD")
AWS_CONSOLE_URL = os.getenv(
    "AWS_CONSOLE_URL", "https://nxtcloud.signin.aws.amazon.com/console"
)

# 생성자 목록 (환경변수에서 로드)
creators_env = os.getenv("CREATORS", "이정훈,김유림,김도겸,이성용")
CREATORS = [creator.strip() for creator in creators_env.split(",")]

# 스택 정보 저장 파일
STACK_INFO_FILE = os.getenv("STACK_INFO_FILE", "stack_info.json")

# 세션 상태 초기화
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "group_name" not in st.session_state:
    st.session_state.group_name = ""
if "user_count" not in st.session_state:
    st.session_state.user_count = 30
if "creator" not in st.session_state:
    st.session_state.creator = CREATORS[0]
if "markdown_content" not in st.session_state:
    st.session_state.markdown_content = ""


def load_stack_info():
    """스택 정보 로드"""
    try:
        if os.path.exists(STACK_INFO_FILE):
            with open(STACK_INFO_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return []
    except:
        return []


def save_stack_info(stack_list):
    """스택 정보 저장"""
    try:
        with open(STACK_INFO_FILE, "w", encoding="utf-8") as f:
            json.dump(stack_list, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False


def add_stack_info(stack_name, group_name, user_count, creator):
    """새 스택 정보 추가"""
    stack_list = load_stack_info()

    new_stack = {
        "stack_name": stack_name,
        "group_name": group_name,
        "user_count": user_count,
        "creator": creator,
        "created_at": datetime.now(pytz.timezone("Asia/Seoul")).strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "stack_id": "",  # CloudFormation 실행 후 업데이트됨
    }

    stack_list.append(new_stack)
    save_stack_info(stack_list)
    return new_stack


def update_stack_id(stack_name, stack_id):
    """스택 ID 업데이트"""
    stack_list = load_stack_info()
    for stack in stack_list:
        if stack["stack_name"] == stack_name:
            stack["stack_id"] = stack_id
            break
    save_stack_info(stack_list)


def remove_stack_info(stack_name):
    """스택 정보 제거"""
    stack_list = load_stack_info()
    stack_list = [stack for stack in stack_list if stack["stack_name"] != stack_name]
    save_stack_info(stack_list)


def authenticate():
    """비밀번호 인증 함수"""
    st.title("🔐 NXTCloud IAM 사용자 생성기")
    st.markdown("---")

    st.warning("⚠️ 보안을 위해 비밀번호를 입력해주세요.")

    password = st.text_input("비밀번호 입력", type="password", key="password_input")

    col1, col2, col3 = st.columns([1, 1, 2])
    with col2:
        if st.button("로그인", type="primary", use_container_width=True):
            if password == ADMIN_PASSWORD:
                st.session_state.authenticated = True
                st.success("✅ 인증 성공!")
                st.rerun()
            else:
                st.error("❌ 잘못된 비밀번호입니다.")


def generate_markdown(group_name, user_count):
    """마크다운 내용 생성"""
    # 사용자 테이블 생성
    user_table = "| Username | IAM User |\n|----------|----------|\n"
    for i in range(user_count + 1):
        iam_user = f"{group_name}-{i:02d}"
        user_table += f"|          | {iam_user} |\n"

    markdown_content = f"""# NXTCloud IAM 계정 정보

## 🔗 로그인 링크
[AWS Console 로그인]({AWS_CONSOLE_URL})

## 🔑 초기 비밀번호
```
{DEFAULT_USER_PASSWORD}
```
⚠️ **주의**: 최초 로그인 시 반드시 비밀번호를 변경해야 합니다.

## 📋 사용 안내
1. 위의 AWS Console 링크를 클릭합니다
2. IAM User 칼럼의 사용자명으로 로그인합니다
3. 초기 비밀번호 `{DEFAULT_USER_PASSWORD}`를 입력합니다
4. 새로운 비밀번호로 변경합니다

## 👥 생성된 계정 목록

{user_table}



"""
    return markdown_content


def execute_cloudformation(group_name, user_count, creator):
    """CloudFormation 스택 배포 실행"""
    try:
        # 스택명 생성
        stack_name = f"nxtcloud-iamuser-{group_name}"

        # 스택 정보 미리 저장
        stack_info = add_stack_info(stack_name, group_name, user_count, creator)

        # CloudFormation 명령어 구성
        cf_template_file = os.getenv(
            "CF_TEMPLATE_FILE", "nxtcloud-iamuser-template.yaml"
        )
        cmd = [
            "aws",
            "cloudformation",
            "create-stack",
            "--stack-name",
            stack_name,
            "--template-body",
            f"file://{cf_template_file}",
            "--parameters",
            f"ParameterKey=GroupName,ParameterValue={group_name}",
            f"ParameterKey=UserCount,ParameterValue={user_count}",
            "--capabilities",
            "CAPABILITY_NAMED_IAM",
        ]

        # 명령어 실행
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.getcwd())

        if result.returncode == 0:
            # 성공 시 스택 ID 추출 및 업데이트
            try:
                output = json.loads(result.stdout)
                if "StackId" in output:
                    update_stack_id(stack_name, output["StackId"])
            except:
                pass
        else:
            # 실패 시 스택 정보 제거
            remove_stack_info(stack_name)

        return result.returncode == 0, result.stdout, result.stderr, stack_name

    except Exception as e:
        return False, "", str(e), ""


def delete_cloudformation_stack(stack_name):
    """CloudFormation 스택 삭제"""
    try:
        cmd = ["aws", "cloudformation", "delete-stack", "--stack-name", stack_name]

        result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.getcwd())

        if result.returncode == 0:
            # 성공 시 스택 정보 제거
            remove_stack_info(stack_name)

        return result.returncode == 0, result.stdout, result.stderr

    except Exception as e:
        return False, "", str(e)


def create_tab():
    """생성 탭"""
    st.subheader("📝 새 IAM 사용자 그룹 생성")

    # 좌측: 입력 폼
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("#### 설정 입력")

        # 생성자 선택
        creator = st.selectbox(
            "생성자",
            options=CREATORS,
            index=(
                CREATORS.index(st.session_state.creator)
                if st.session_state.creator in CREATORS
                else 0
            ),
        )

        # 그룹명 입력
        group_name = st.text_input(
            "그룹명",
            value=st.session_state.group_name,
            placeholder="예: developers, students, test-group",
            help="영문, 숫자, 하이픈(-), 언더스코어(_) 사용 가능",
        )

        # 사용자 수 입력
        user_count = st.number_input(
            "최대 사용자 번호",
            min_value=1,
            max_value=100,
            value=st.session_state.user_count,
            help="30 입력시 00~30까지 총 31명 생성됩니다",
        )

        # 미리보기
        if group_name:
            st.info(
                f"👀 **미리보기**: {group_name}-00 ~ {group_name}-{user_count:02d} (총 {user_count + 1}명)"
            )

        # 마크다운 생성 버튼
        if st.button("📄 계정 정보 생성", type="primary", use_container_width=True):
            if group_name:
                st.session_state.group_name = group_name
                st.session_state.user_count = user_count
                st.session_state.creator = creator
                st.session_state.markdown_content = generate_markdown(
                    group_name, user_count
                )
                st.success("✅ 계정 정보가 생성되었습니다!")
            else:
                st.error("❌ 그룹명을 입력해주세요.")

    with col2:
        st.markdown("#### 생성된 계정 정보")

        if st.session_state.markdown_content:
            # 복사용 텍스트만 표시
            st.text_area(
                "복사용 텍스트",
                value=st.session_state.markdown_content,
                height=400,
                help="내용을 선택하고 Ctrl+C로 복사하세요",
            )
        else:
            st.info("👈 왼쪽에서 설정을 입력하고 '계정 정보 생성' 버튼을 클릭하세요.")

    # 실행 섹션
    if st.session_state.markdown_content:
        st.markdown("---")
        st.subheader("🚀 CloudFormation 스택 배포")

        col3, col4, col5 = st.columns([1, 2, 1])

        with col4:
            st.warning("⚠️ **주의**: 이 작업은 실제 AWS 리소스를 생성합니다.")

            if st.button(
                "🛠️ CloudFormation 스택 배포 실행",
                type="secondary",
                use_container_width=True,
            ):
                with st.spinner("CloudFormation 스택을 배포하는 중..."):
                    success, stdout, stderr, stack_name = execute_cloudformation(
                        st.session_state.group_name,
                        st.session_state.user_count,
                        st.session_state.creator,
                    )

                if success:
                    st.success(
                        "✅ CloudFormation 스택 배포가 성공적으로 시작되었습니다!"
                    )
                    st.code(stdout, language="json")
                    st.info(f"📝 스택 정보가 저장되었습니다: {stack_name}")
                else:
                    st.error("❌ CloudFormation 스택 배포에 실패했습니다.")
                    st.code(stderr, language="text")

                    # 도움말 표시
                    st.info(
                        """
                    **배포 실패 시 확인사항:**
                    1. AWS CLI가 설치되고 구성되어 있는지 확인
                    2. 적절한 IAM 권한이 있는지 확인
                    3. 템플릿 파일이 같은 디렉토리에 있는지 확인
                    4. 그룹명이 AWS 규칙에 맞는지 확인
                    """
                    )


def manage_tab():
    """관리 탭"""
    st.subheader("📊 생성된 스택 관리")

    # 스택 목록 로드
    stack_list = load_stack_info()

    if not stack_list:
        st.info("생성된 스택이 없습니다. '생성' 탭에서 새 스택을 만들어보세요.")
        return

    # 최신순으로 정렬 (created_at 기준 내림차순)
    stack_list = sorted(stack_list, key=lambda x: x.get("created_at", ""), reverse=True)

    # 스택 목록 테이블 표시
    st.markdown("#### 생성된 스택 목록")

    for i, stack in enumerate(stack_list):
        with st.container():
            col1, col2, col3 = st.columns([3, 1, 1])

            with col1:
                st.markdown(
                    f"""
                **🏷️ {stack['group_name']}** 
                - **생성자**: {stack['creator']}
                - **인원수**: {stack['user_count'] + 1}명 ({stack['group_name']}-00 ~ {stack['group_name']}-{stack['user_count']:02d})
                - **생성일시**: {stack['created_at']}
                - **스택명**: {stack['stack_name']}
                - **스택 ID**: {stack.get('stack_id', 'N/A')}
                """
                )

            with col2:
                # 상태 확인 버튼
                if st.button("🔍 상태 확인", key=f"status_{i}"):
                    with st.spinner("스택 상태 확인 중..."):
                        cmd = [
                            "aws",
                            "cloudformation",
                            "describe-stacks",
                            "--stack-name",
                            stack["stack_name"],
                        ]
                        result = subprocess.run(cmd, capture_output=True, text=True)

                        if result.returncode == 0:
                            try:
                                output = json.loads(result.stdout)
                                stack_status = output["Stacks"][0]["StackStatus"]
                                st.success(f"스택 상태: {stack_status}")
                            except:
                                st.error("스택 상태 확인 실패")
                        else:
                            st.error("스택을 찾을 수 없습니다")

            with col3:
                # 삭제 버튼
                if st.button("🗑️ 삭제", key=f"delete_{i}", type="secondary"):
                    st.session_state[f"confirm_delete_{i}"] = True

                # 삭제 확인
                if st.session_state.get(f"confirm_delete_{i}", False):
                    st.warning("⚠️ 정말 삭제하시겠습니까?")

                    col_yes, col_no = st.columns(2)
                    with col_yes:
                        if st.button("✅ 예", key=f"yes_{i}"):
                            with st.spinner("스택 삭제 중..."):
                                success, stdout, stderr = delete_cloudformation_stack(
                                    stack["stack_name"]
                                )

                            if success:
                                st.success("✅ 스택 삭제가 시작되었습니다!")
                                st.rerun()
                            else:
                                st.error("❌ 스택 삭제에 실패했습니다.")
                                st.code(stderr, language="text")

                            st.session_state[f"confirm_delete_{i}"] = False

                    with col_no:
                        if st.button("❌ 아니오", key=f"no_{i}"):
                            st.session_state[f"confirm_delete_{i}"] = False
                            st.rerun()

            st.markdown("---")


def main_interface():
    """메인 인터페이스"""
    st.title("👥 NXTCloud IAM 사용자 생성기")

    # 탭 생성
    tab1, tab2 = st.tabs(["📝 생성", "📊 관리"])

    with tab1:
        create_tab()

    with tab2:
        manage_tab()


def main():
    """메인 함수"""
    if not st.session_state.authenticated:
        authenticate()
    else:
        main_interface()

        # 로그아웃 버튼
        st.sidebar.markdown("---")
        if st.sidebar.button("🚪 로그아웃"):
            st.session_state.authenticated = False
            st.session_state.group_name = ""
            st.session_state.user_count = 30
            st.session_state.creator = CREATORS[0]
            st.session_state.markdown_content = ""
            st.rerun()


if __name__ == "__main__":
    main()
