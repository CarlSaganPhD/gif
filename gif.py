from importlib import import_module
import io

from matplotlib import pyplot as plt
from PIL import Image

try:
    from altair_saver import save as save_alt

    altair_saver_installed = True
except ModuleNotFoundError:
    altair_saver_installed = False


class MissingExtension(Exception):
    pass


def frame(*save_args, **save_kwargs):
    """
    Decorator for a matplotlib plot function.

    Usage (matplotlib):
    ```
    @gif.frame(*save_args, **save_kwargs)
    def plot(i):
        xi = x[i*10:(i+1)*10]
        yi = y[i*10:(i+1)*10]
        plt.scatter(xi, yi)
        plt.xlim((0, 100))
        plt.ylim((0, 100))
    ```

    Usage (Altair):
    ```
    @gif.frame(*save_args, **save_kwargs)
    def plot(i):
        d = df[df['t'] == i]
        chart = alt.Chart(d).encode(
            x=alt.X('x', scale=alt.Scale(domain=(0, 100))),
            y=alt.Y('y', scale=alt.Scale(domain=(0, 100)))
        ).mark_circle()
        return chart
    ```

    Use the `save_args` and `save_kwargs` to pass additional arguments such
    as the dpi to the `plt.save()` and `altair_saver.save()` methods.
    """
    def wrapper1(func):
        def wrapper2(*args, **kwargs):
            buffer = io.BytesIO()
            plot = func(*args, **kwargs)
            if "altair" in str(type(plot)):
                if not altair_saver_installed:
                    raise MissingExtension("pip install gif[altair]")
                save_alt(plot, buffer, fmt="png", *save_args, **save_kwargs)
            else:
                plt.savefig(buffer, format="png", *save_args, **save_kwargs)
                plt.close()
            buffer.seek(0)
            image = Image.open(buffer)
            return image

        return wrapper2
    return wrapper1


def save(frames, path, duration=100):
    """
    Save decorated frames to an animated gif.

    - frames (list): collection of frames built with the frame decorator
    - path (str): filename with relative or absolute path
    - duration (int): milliseconds between frames

    Example:
    ```
    frames = []
    for i in range(10):
        frame = plot(i)
        frames.append(frame)
    ```
    """
    frames[0].save(
        path,
        save_all=True,
        append_images=frames[1:],
        optimize=True,
        duration=duration,
        loop=0,
    )
