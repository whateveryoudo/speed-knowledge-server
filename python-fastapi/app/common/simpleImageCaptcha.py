from captcha.image import ImageCaptcha


class SimpleImageCaptcha(ImageCaptcha):
    def create_noise_curve(self, image, color):
        # 不画干扰曲线
        return image

    def create_noise_dots(self, image, color, number=30):
        # 不画噪点
        return image

    def transform(self, image):
        # 不做扭曲变换
        return image
