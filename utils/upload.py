"""图片上传处理"""

import os
import uuid
from werkzeug.utils import secure_filename
from config import config
from PIL import Image


def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in config.ALLOWED_EXTENSIONS


def save_photo(file, subfolder='items'):
    """
    保存上传的图片，自动缩放到最大800px宽度
    返回相对于 static/ 的路径
    """
    if not file or not allowed_file(file.filename):
        return '', '不支持的文件格式，仅支持: png, jpg, jpeg, gif, webp'

    # 生成唯一文件名
    ext = file.filename.rsplit('.', 1)[1].lower()
    unique_name = f"{uuid.uuid4().hex}.{ext}"

    # 确保目标目录存在
    upload_dir = os.path.join(config.UPLOAD_FOLDER, subfolder)
    os.makedirs(upload_dir, exist_ok=True)

    save_path = os.path.join(upload_dir, unique_name)

    try:
        # 保存原图
        file.save(save_path)

        # 使用 Pillow 缩放图片
        img = Image.open(save_path)
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')

        max_width = 800
        if img.width > max_width:
            ratio = max_width / img.width
            new_height = int(img.height * ratio)
            img = img.resize((max_width, new_height), Image.LANCZOS)

        img.save(save_path, quality=85, optimize=True)

        # 返回相对于static的路径
        relative_path = f"uploads/{subfolder}/{unique_name}"
        return relative_path, None

    except Exception as e:
        # 清理失败的保存
        if os.path.exists(save_path):
            os.remove(save_path)
        return '', f'图片保存失败: {str(e)}'


def delete_photo(relative_path):
    """删除已上传的图片"""
    if not relative_path:
        return
    full_path = os.path.join(config.BASE_DIR, 'static', relative_path)
    if os.path.exists(full_path):
        os.remove(full_path)
