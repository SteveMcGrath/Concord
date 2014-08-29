from StringIO import StringIO
import base64
import qrcode


def qrgen(ticket_id, encode=False):
    imgbuf = StringIO()
    imgraw = qrcode.make('http://ticket/%s' % ticket_id)
    imgraw.save(imgbuf, 'PNG')
    response = imgbuf.getvalue()
    imgbuf.close()
    if encode:
        return base64.b64encode(response)
    else:
        return response