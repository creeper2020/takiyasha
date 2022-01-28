import os
from fnmatch import fnmatch
from typing import IO, Optional

from .typehints import BytesType, PathType

SUPPORTED_FORMATS_PATTERNS: dict[str, list[str]] = {
    'ncm': ['*.ncm'],
    'qmc': ['*.qmc[023468]', '*.qmcflac', '*.qmcogg',
            '*.tkm',
            '*.mflac', '*.mflac[0]', '*.mgg', '*.mgg[01l]',
            '*.bkcmp3', '*.bkcm4a', '*.bkcflac', '*.bkcwav', '*.bkcape', '*.bkcogg', '*.bkcwma']
}

AUDIO_FILE_HEADER_FORMAT_MAP: dict[bytes, str] = {
    b'fLaC': 'flac',
    b'ID3': 'mp3',
    b'OggS': 'ogg',
    b'ftyp': 'm4a',
    b'0&\xb2u\x8ef\xcf\x11\xa6\xd9\x00\xaa\x00b\xcel': 'wma',
    b'RIFF': 'wav',
    b'\xff\xf1': 'aac',
    b'FRM8': 'dff',
    b'MAC ': 'ape'
}
AUDIO_FILE_FORMAT_HEADER_MAP: dict[str, bytes] = {
    v: k for k, v in AUDIO_FILE_HEADER_FORMAT_MAP.items()
}
IMAGE_FILE_HEADER_MIME_MAP: dict[bytes, str] = {
    b'\x89\x50\x4e\x47\x0d\x0a\x1a\x0a': 'image/png',
    b'\xff\xd8\xff': 'image/jpeg',
    b'\x42\x4d': 'image/bmp'
}
IMAGE_FILE_MIME_HEADER_MAP: dict[str, bytes] = {
    v: k for k, v in IMAGE_FILE_HEADER_MIME_MAP.items()
}


def get_audio_format(data: BytesType) -> Optional[str]:
    for header, fmt in AUDIO_FILE_HEADER_FORMAT_MAP.items():
        if data.startswith(header):
            return fmt


def get_possible_audio_header(fmt: str) -> Optional[bytes]:
    fmt: str = fmt.removeprefix('.')
    return AUDIO_FILE_FORMAT_HEADER_MAP.get(fmt)


def get_image_mime(data: BytesType) -> Optional[str]:
    for header, fmt in IMAGE_FILE_HEADER_MIME_MAP.items():
        if data.startswith(header):
            return fmt


def get_possible_image_header(fmt: str) -> Optional[bytes]:
    fmt: str = fmt.removeprefix('.')
    return IMAGE_FILE_MIME_HEADER_MAP.get(fmt)


def get_file_ext(name: PathType) -> str:
    return os.path.splitext(name)[1]


def get_encryption_format(name: PathType) -> Optional[str]:
    for enctype, patterns in SUPPORTED_FORMATS_PATTERNS.items():
        for pattern in patterns:
            if fnmatch(name, pattern):
                return enctype


def is_fileobj(fileobj: IO[bytes]) -> bool:
    return not isinstance(fileobj, (str, bytes)) and not hasattr(fileobj, "__fspath__")


def raise_while_not_fileobj(
        fileobj: IO[bytes],
        *,
        readable=True,
        seekable=True,
        writable=False
) -> None:
    if readable:
        try:
            data = fileobj.read(0)
        except Exception:
            if not hasattr(fileobj, "read"):
                raise ValueError(f"{fileobj} not a valid file object")
            raise ValueError(f"cannot read from file object {fileobj}")

        if not isinstance(data, bytes):
            raise ValueError(f"file object {fileobj} not opened in binary mode")

    if seekable:
        try:
            fileobj.seek(0, os.SEEK_END)
        except Exception:
            if not hasattr(fileobj, "seek"):
                raise ValueError(f"{fileobj} not a valid file object")
            raise ValueError(f"cannot seek in file object {fileobj}")

    if writable:
        try:
            fileobj.write(b"")
        except Exception:
            if not hasattr(fileobj, "write"):
                raise ValueError(f"{fileobj} not a valid file object")
            raise ValueError(f"cannot write to file object {fileobj}")


def get_file_name_from_fileobj(fileobj: IO[bytes]):
    name = getattr(fileobj, 'name', '')
    if not isinstance(name, (str, bytes)):
        return str(name)
    return name


def xor_bytestrings(term1: BytesType, term2: BytesType) -> bytes:
    if len(term1) != len(term2):
        raise ValueError('Only byte strings of equal length can be xored')

    return bytes(b1 ^ b2 for b1, b2 in zip(term1, term2))
