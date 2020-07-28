
# Basic progress bar for the downloading procedures for urllib.request.urlretrieve


def progress_bar(batch=None, batchsize=None, filesize=None, **kwargs):

    barsize = 50
    prog = batch*batchsize/filesize if not kwargs else kwargs['downloaded']/kwargs['totalsize']
    compl = round(prog*100, 1) if prog < 1 else 100
    prog_size = int(prog * barsize)

    print("\r[{0}{1:3.1f}%{2}]".format(chr(9608)*prog_size, compl, '.'*(barsize-prog_size)),

          "{} / {} Bytes".format(batch*batchsize if prog < 1 else filesize, filesize) if not kwargs

          else "{} / {} Bytes".format(kwargs['downloaded'], kwargs['totalsize']),

          flush=True, end='')
