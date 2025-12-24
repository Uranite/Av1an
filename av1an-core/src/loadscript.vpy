import os
import vapoursynth as vs
core = vs.core

source = os.environ.get("AV1AN_SOURCE", None)
chunk_method = os.environ.get("AV1AN_CHUNK_METHOD", None)
perform_scene_detection = globals().get("AV1AN_PERFORM_SCENE_DETECTION", None)

# Default valid chunk methods
VALID_CHUNK_METHODS: list[str] = ["lsmash", "ffms2", "dgdecnv", "bestsource"]

# Ensure chunk_method is valid
if chunk_method not in VALID_CHUNK_METHODS:
    raise ValueError(f"Invalid chunk method: {chunk_method}")

# Check if source is provided
if not source:
    raise ValueError("Source path not provided")

# Ensure source exists
if not os.path.exists(source):
    raise ValueError("Source path does not exist")

# Import video
match (chunk_method):  # type: ignore
    case "lsmash":
        video = core.lsmas.LWLibavSource(source)
    case "ffms2":
        video = core.ffms2.Source(source)
    case "dgdecnv":
        video = core.dgdecodenv.DGSource(source)
    case "bestsource":
        # bestsource has the default behavior to store its index files in a user-specific directory
        # but for consistency, this setting makes it store the index file next to the video
        # as all the other source filters do
        video = core.bs.VideoSource(source, cachepath="/")

if perform_scene_detection is None:
    # Limit decoder resources when encoding since we will have multiple workers running
    core.num_threads = 1
    core.max_cache_size = 1024


# Output video
select_every = globals().get("AV1AN_SELECT_EVERY", None)
if select_every is not None:
    video = video.std.SelectEvery(cycle=int(select_every), offsets=0)

pixel_format = globals().get("AV1AN_PIX_FMT", None)
if pixel_format is not None:
    fmt_map = {
        "yuv420p": vs.YUV420P8,
        "yuv422p": vs.YUV422P8,
        "yuv444p": vs.YUV444P8,
        "yuv410p": vs.YUV410P8,
        "yuv411p": vs.YUV411P8,
        "yuv440p": vs.YUV440P8,
        "yuv420p9le": vs.YUV420P9,
        "yuv422p9le": vs.YUV422P9,
        "yuv444p9le": vs.YUV444P9,
        "yuv420p10le": vs.YUV420P10,
        "yuv422p10le": vs.YUV422P10,
        "yuv444p10le": vs.YUV444P10,
        "yuv420p12le": vs.YUV420P12,
        "yuv422p12le": vs.YUV422P12,
        "yuv444p12le": vs.YUV444P12,
        "yuv420p14le": vs.YUV420P14,
        "yuv422p14le": vs.YUV422P14,
        "yuv444p14le": vs.YUV444P14,
        "yuv420p16le": vs.YUV420P16,
        "yuv422p16le": vs.YUV422P16,
        "yuv444p16le": vs.YUV444P16,
        "rgb24": vs.RGB24,
        "rgb27le": vs.RGB27,
        "rgb30le": vs.RGB30,
        "rgb48le": vs.RGB48,
    }
    
    fmt = fmt_map.get(pixel_format)
    if fmt is None:
        try:
            fmt = getattr(vs, pixel_format.upper())
        except AttributeError:
             pass

    if fmt is not None:
        video = video.resize.Bicubic(format=fmt)
    else:
        raise ValueError(f"Unsupported or unknown pixel format: {pixel_format}")

video.set_output()
