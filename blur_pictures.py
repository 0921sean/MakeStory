import cv2

# 1. 이미지 파일 경로 지정
input_path = 'kora_valley_pictures/input_image/plan_75.png'   # 사용자가 넣은 이미지 경로
output_path = 'kora_valley_pictures/blurred_image/plan_75_blurred.png'  # 결과 저장 파일 이름

# 2. 이미지 읽기
image = cv2.imread(input_path)

if image is None:
    print("이미지를 불러올 수 없습니다. 경로를 확인해주세요.")
else:
    # 3. 블러 처리 (GaussianBlur 또는 일반 blur 가능)
    blurred = cv2.GaussianBlur(image, (71, 71), 0)

    # 4. 결과 이미지 저장
    cv2.imwrite(output_path, blurred)
    print(f"블러 처리된 이미지를 '{output_path}'에 저장했습니다.")

    # 5. 이미지 출력 (선택사항)
    cv2.imshow('Blurred Image', blurred)
    cv2.waitKey(0)
    cv2.destroyAllWindows()