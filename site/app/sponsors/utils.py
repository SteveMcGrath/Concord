from PIL import Image
from flask import current_app
from StringIO import StringIO
import numpy as np
from os import path


def alpha_composite(src, dst):
    '''
    Return the alpha composite of src and dst.

    Parameters:
    src -- PIL RGBA Image object
    dst -- PIL RGBA Image object

    The algorithm comes from http://en.wikipedia.org/wiki/Alpha_compositing
    '''
    # http://stackoverflow.com/a/3375291/190597
    # http://stackoverflow.com/a/9166671/190597
    src = np.asarray(src)
    dst = np.asarray(dst)
    out = np.empty(src.shape, dtype = 'float')
    alpha = np.index_exp[:, :, 3:]
    rgb = np.index_exp[:, :, :3]
    src_a = src[alpha]/255.0
    dst_a = dst[alpha]/255.0
    out[alpha] = src_a+dst_a*(1-src_a)
    old_setting = np.seterr(invalid = 'ignore')
    out[rgb] = (src[rgb]*src_a + dst[rgb]*dst_a*(1-src_a))/out[alpha]
    np.seterr(**old_setting)    
    out[alpha] *= 255
    np.clip(out,0,255)
    # astype('uint8') maps np.nan (and np.inf) to 0
    out = out.astype('uint8')
    out = Image.fromarray(out, 'RGBA')
    return out


def save_image(raw_image, ):
    buff = StringIO()
    buff.write(raw_image)
    buff.seek(0)
    img = Image.open(buff).convert('RGBA')
    img.thumbnail(current_app.config['SPONSOR_IMAGE_SIZE'])
    bg = Image.new('RGBA', size=img.size, color=current_app.config['SPONSOR_IMAGE_BACKGROUND'])
    img = alpha_composite(img, bg)
    img.save(path.join(current_app.config['SPONSOR_IMAGE_FOLDER'], ))