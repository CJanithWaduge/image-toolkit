from __future__ import annotations

import logging
import subprocess
from pathlib import Path
from typing import Callable, Optional

from .converter import Converter
from .upscaler import Upscaler, UpscalingError
from .models import ImageJob, JobResult

logger = logging.getLogger(__name__)

ProgressCallback = Callable[[str], None]


class ProcessingPipeline:
    """Orchestrates conversion (and optionally upscaling) for a single job."""

    def __init__(self, converter: Converter, upscaler: Upscaler) -> None:
        self.converter = converter
        self.upscaler = upscaler

    def process(
        self, job: ImageJob, on_progress: Optional[ProgressCallback] = None
    ) -> JobResult:
        log = on_progress or (lambda _: None)

        try:
            self.converter.configure(job.mode)
            ext = self.converter.target_ext
            base_path = Path(job.output_dir) / f"{job.output_name}{ext}"

            if job.upscale_enabled:
                temp_path = Path(job.output_dir) / f"__temp_{job.output_name}{ext}"
                temp_path_str, final_path_str = str(temp_path), str(base_path)

                log(f"Converting: {job.output_name}")
                self.converter.convert(job.source_path, temp_path_str)

                log(f"Upscaling: {job.output_name}")
                self.upscaler.upscale(temp_path_str, final_path_str)
                temp_path.unlink(missing_ok=True)

                return JobResult(success=True, output_path=final_path_str)
            else:
                output_path = str(base_path)
                log(f"Converting: {job.output_name}")
                self.converter.convert(job.source_path, output_path)
                return JobResult(success=True, output_path=output_path)

        except subprocess.TimeoutExpired:
            return JobResult(success=False, error=f"{job.output_name}: timed out")
        except UpscalingError as e:
            return JobResult(success=False, error=str(e))
        except Exception as e:
            logger.exception("Pipeline failure for %s", job.output_name)
            return JobResult(success=False, error=f"{job.output_name}: {e}")
