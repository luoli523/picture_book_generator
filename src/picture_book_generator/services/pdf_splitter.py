"""PDF分割服务 - 将Slides PDF拆分为单页图片"""

from __future__ import annotations

from pathlib import Path

try:
    import fitz  # PyMuPDF

    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False


class PDFSplitterService:
    """将PDF文件拆分为单页PNG图片"""

    DEFAULT_DPI = 200

    def __init__(self, dpi: int = DEFAULT_DPI):
        self.dpi = dpi

    def _check_dependency(self):
        if not PYMUPDF_AVAILABLE:
            raise ImportError(
                "PyMuPDF 未安装。请运行:\n"
                "  pip install -r requirements.txt"
            )

    def split(self, pdf_path: str, output_dir: str | None = None) -> list[str]:
        """将PDF拆分为单页PNG图片

        Args:
            pdf_path: PDF文件路径
            output_dir: 输出目录，默认为 PDF 所在目录下的同名子文件夹

        Returns:
            生成的图片路径列表
        """
        self._check_dependency()

        pdf = Path(pdf_path)
        if not pdf.exists():
            raise FileNotFoundError(f"PDF文件不存在: {pdf_path}")

        if output_dir is None:
            out = pdf.parent / pdf.stem
        else:
            out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)

        zoom = self.dpi / 72
        matrix = fitz.Matrix(zoom, zoom)

        image_paths: list[str] = []
        doc = fitz.open(str(pdf))
        try:
            for i, page in enumerate(doc):
                pix = page.get_pixmap(matrix=matrix)
                img_path = out / f"page_{i + 1:02d}.png"
                pix.save(str(img_path))
                image_paths.append(str(img_path))
        finally:
            doc.close()

        return image_paths
