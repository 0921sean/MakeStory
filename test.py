# 사진 컬러에서 흑백으로
from PIL import Image
def convert_to_grayscale(image_path, output_path):
    # 이미지 열기
    image = Image.open(image_path)
    
    # 흑백으로 변환
    grayscale_image = image.convert("L")
    
    # 변환된 이미지 저장
    grayscale_image.save(output_path)
    print(f"이미지를 흑백으로 변환하여 '{output_path}'에 저장했습니다.")
# 사용 예시
if __name__ == "__main__":
    input_image_path = '00.jpg'  # 입력 이미지 경로
    output_image_path = 'profile_image.jpg'  # 출력 이미지 경로
    
    convert_to_grayscale(input_image_path, output_image_path)