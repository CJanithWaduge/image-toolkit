import os
import subprocess
from typing import Callable, Optional

from .converter import Converter
from .upscaler import Upscaler
from .models import ImageJob, JobResult


ProgressCallback = Callable[[str], None]


class ProcessingPipeline:
    def __init__(self, converter: Converter, upscaler: Upscaler):
        self.converter = converter
        self.upscaler = upscaler

    def process(self, job: ImageJob, on_progress: Optional[ProgressCallback] = None) -> JobResult:
        log = on_progress or (lambda _: None)

        try:
            if job.upscale_enabled:
                scale = job.upscale_scale
                self.converter.configure(job.mode)
                ext = self.converter.target_ext
                temp_path = os.path.join(job.output_dir, f"__temp_{job.output_name}{ext}")
                final_path = os.path.join(job.output_dir, f"{job.output_name}_{scale}x{ext}")

                log(f"Converting: {job.output_name}")
                self.converter.convert(job.source_path, temp_path)

                log(f"Upscaling: {job.output_name}")
                self.upscaler.upscale(temp_path, final_path)
                os.remove(temp_path)

                return JobResult(success=True, output_path=final_path)
            else:
                self.converter.configure(job.mode)
                ext = self.converter.target_ext
                output_path = os.path.join(job.output_dir, f"{job.output_name}{ext}")

                log(f"Converting: {job.output_name}")
                self.converter.convert(job.source_path, output_path)

                return JobResult(success=True, output_path=output_path)

        except subprocess.TimeoutExpired:
            return JobResult(success=False, error=f"{job.output_name}: timed out")
        except Exception as e:
            return JobResult(success=False, error=f"{job.output_name}: {e}")
