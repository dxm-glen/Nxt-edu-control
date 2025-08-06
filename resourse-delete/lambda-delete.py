import boto3

### 지워야하는 리소스 키워드 ###
keyword = "group-"

### 대상 리전 지정 ###
region_name = "us-east-1"


def delete_lambda_functions(keyword):
    # 서울 리전 세션 생성
    session = boto3.Session(region_name=region_name)

    # Lambda 클라이언트 생성
    lambda_client = session.client("lambda")

    # Lambda 함수 목록 가져오기
    response = lambda_client.list_functions()

    print("시작\n\n\n")
    # 이름에 키워드가 포함된 함수 찾기
    functions_to_delete = [
        function["FunctionName"]
        for function in response.get("Functions", [])
        if keyword in function["FunctionName"].lower()
    ]

    if functions_to_delete:
        print("찾은 Lambda 함수 목록:")
        for function_name in functions_to_delete:
            print(f"- {function_name}")

        confirmation = (
            input("이 모든 Lambda 함수를 삭제하시겠습니까? (y/n): ").strip().lower()
        )
        if confirmation == "y":
            for function_name in functions_to_delete:
                print(f"\n\nLambda 함수 삭제 중: {function_name}")
                lambda_client.delete_function(FunctionName=function_name)
        else:
            for function_name in functions_to_delete:
                confirmation = (
                    input(
                        f"Lambda 함수 '{function_name}'을(를) 삭제하시겠습니까? (y/n): "
                    )
                    .strip()
                    .lower()
                )
                if confirmation == "y":
                    print(f"\n\nLambda 함수 삭제 중: {function_name}")
                    lambda_client.delete_function(FunctionName=function_name)
    else:
        print("지정된 키워드가 포함된 함수를 찾을 수 없습니다.")

    print("\n\n\n종료")


if __name__ == "__main__":
    delete_lambda_functions(keyword)
