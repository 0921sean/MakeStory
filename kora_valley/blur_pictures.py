"""
이미지 가우시안 블러 처리

지정한 이미지에 가우시안 블러를 적용하여 저장합니다.

사용법:
    python blur_pictures.py                                           # 기본 경로 사용
    python blur_pictures.py --input img.png --output img_blurred.png  # 경로 지정
"""

import argparse
import os

import cv2

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def blur_image(input_path, output_path, kernel_size=71):
    """이미지에 가우시안 블러를 적용하여 저장합니다."""
    image = cv2.imread(input_path)

    if image is None:
        print("이미지를 불러올 수 없습니다. 경로를 확인해주세요.")
        return False

    blurred = cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    cv2.imwrite(output_path, blurred)
    print(f"블러 처리된 이미지를 '{output_path}'에 저장했습니다.")
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="이미지에 가우시안 블러를 적용합니다.")
    parser.add_argument("--input", "-i", default=os.path.join(BASE_DIR, "input_image", "plan_339.png"),
                        help="입력 이미지 경로")
    parser.add_argument("--output", "-o", default=os.path.join(BASE_DIR, "blurred_image", "plan_339_blurred.png"),
                        help="출력 이미지 경로")
    parser.add_argument("--kernel", "-k", type=int, default=71,
                        help="블러 커널 크기 (홀수, 기본: 71)")
    args = parser.parse_args()

    blur_image(args.input, args.output, args.kernel)