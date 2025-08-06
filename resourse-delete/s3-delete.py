import boto3

### 지워야하는 리소스 키워드 ###
keyword = "group-"

### 대상 리전 지정 ###
region_name = "us-east-1"


def delete_s3_buckets(keyword):
    # 서울 리전 세션 생성
    session = boto3.Session(region_name=region_name)

    # S3 클라이언트 생성
    s3 = session.client("s3")
    s3_resource = session.resource("s3")

    # 버킷 목록 가져오기
    response = s3.list_buckets()

    print("시작\n\n\n")
    # 이름에 키워드가 포함된 버킷 찾기
    buckets_to_delete = [
        bucket["Name"]
        for bucket in response.get("Buckets", [])
        if keyword in bucket["Name"].lower()
    ]

    if buckets_to_delete:
        print("찾은 S3 버킷 목록:")
        for bucket_name in buckets_to_delete:
            print(f"- {bucket_name}")

        confirmation = (
            input("이 모든 S3 버킷을 삭제하시겠습니까? (y/n): ").strip().lower()
        )
        if confirmation == "y":
            for bucket_name in buckets_to_delete:
                print(f"\n\nS3 버킷의 모든 객체를 삭제 중: {bucket_name}")
                # 버킷 비우기
                bucket_resource = s3_resource.Bucket(bucket_name)
                bucket_resource.objects.delete()

                # 버킷 버전이 활성화된 경우 모든 버전 삭제
                bucket_versioned = s3_resource.Bucket(bucket_name)
                bucket_versioned.object_versions.delete()

                print(f"\n\nS3 버킷 삭제 중: {bucket_name}")
                s3.delete_bucket(Bucket=bucket_name)
        else:
            for bucket_name in buckets_to_delete:
                confirmation = (
                    input(
                        f"\n\nS3 버킷 '{bucket_name}'을(를) 삭제하시겠습니까? (y/n): "
                    )
                    .strip()
                    .lower()
                )
                if confirmation == "y":
                    print(f"\n\nS3 버킷의 모든 객체를 삭제 중: {bucket_name}")
                    # 버킷 비우기
                    bucket_resource = s3_resource.Bucket(bucket_name)
                    bucket_resource.objects.delete()

                    # 버킷 버전이 활성화된 경우 모든 버전 삭제
                    bucket_versioned = s3_resource.Bucket(bucket_name)
                    bucket_versioned.object_versions.delete()

                    print(f"\n\nS3 버킷 삭제 중: {bucket_name}")
                    s3.delete_bucket(Bucket=bucket_name)
    else:
        print("지정된 키워드가 포함된 버킷을 찾을 수 없습니다.")

    print("\n\n\n종료")


if __name__ == "__main__":
    delete_s3_buckets(keyword)
