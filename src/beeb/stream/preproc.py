import ffmpeg
from glob import glob

def mp4_to_wav(input_mp4, sr="16k", output_wav=None):
    """
    Convert an MP4 file to a WAV file at sampling rate `sr` (default 16 kHz).
    If output_dir is None (default), place it in `input_mp4`'s parent
    """
    if output_wav is None:
        output_wav_name = input_mp4.stem + ".wav"
        output_wav = input_mp4.parent / output_wav_name
    ffmpeg.input(filename=input_mp4).output(
        filename=output_wav, ac=2, ar=sr, format="wav"
    ).run(quiet=True)
    return output_wav

def gather_m4s_to_mp4(dash_file, m4s_files, output_mp4):
    """
    Concatenate `.dash` and `.m4s` files using the system `cat` facility.
    """
    if output_mp4.exists():
        raise ValueError(f"{output_mp4=} already exists: risk of doubled output")
    with open(output_mp4, "ab") as f:
        for mpeg in [dash_file, *m4s_files]:
            with open(mpeg, "rb") as part_f:
                f.write(part_f.read())

def gather_pulled_downloads(input_dir, output_dir, filename_stem):
    """
    Gather MPEG stream files from input_dir into a single MP4 file in output_dir
    """
    dash_globstr = f"{input_dir.absolute() / '*.dash'}"
    dash_glob = glob(dash_globstr)
    if len(dash_glob) < 1:
        raise ValueError(f"No dash file found in {input_dir}")
    elif len(dash_glob) > 1:
        raise ValueError(f"Multiple dash files found in {input_dir}")
    else:
        dash_file = dash_glob[0]
    m4s_globstr = f"{input_dir.absolute() / '*.m4s'}"
    m4s_files = sorted(glob(m4s_globstr))
    output_mp4 = output_dir.absolute() / f"{filename_stem}.mp4"
    gather_m4s_to_mp4(dash_file, m4s_files, output_mp4)
    return output_mp4
