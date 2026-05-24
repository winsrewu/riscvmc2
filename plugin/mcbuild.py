import shutil
import hashlib
import json
import subprocess
from pathlib import Path
from beet import Context

MCB_CONFIG_FILE = "mcb.config.js"


def build_mcb(ctx: Context):
    """
    Special thanks to https://github.com/SnaveSutit/mcb-beet.
    """

    def create_source_hash(source: Path, config: Path) -> str:
        hasher = hashlib.sha256()

        def update_from_file(path: Path):
            assert path.is_file()
            hasher.update(path.as_posix().encode())
            hasher.update(path.read_bytes())
            with open(path, "rb") as f:
                hasher.update(f.read())

        def update_from_directory(path: Path):
            assert path.is_dir()
            hasher.update(path.as_posix().encode())
            for path in sorted(path.iterdir()):
                if path.is_file():
                    update_from_file(path)
                elif path.is_dir():
                    update_from_directory(path)

        update_from_file(config)

        if source.is_file():
            update_from_file(source)
        elif source.is_dir():
            update_from_directory(source)

        return hasher.hexdigest()

    config = ctx.directory / MCB_CONFIG_FILE
    build_dir = ctx.cache["mcbuild"].directory / "datapack"
    previous_source_hash = ctx.cache["mcbuild"].json.get("source_hash", None)
    source_dir = ctx.directory / "src" / "mcbuild"

    if not config.exists():
        raise ValueError(f"Config file {config} does not exist.")

    source_hash = create_source_hash(ctx.directory, config)

    # Check if the source has changed
    if source_hash == previous_source_hash:
        if (build_dir / "data").exists():
            ctx.data.load(build_dir)
            return

    # Cleanup
    shutil.rmtree(build_dir, ignore_errors=True)

    # Copy sources
    shutil.copytree(
        source_dir / "mcb",
        build_dir / "src",
        dirs_exist_ok=True,
    )

    shutil.copytree(
        source_dir / "lib" / "bitwise_ops" / "scoreboard",
        build_dir / "src",
        dirs_exist_ok=True,
    )

    shutil.copytree(
        source_dir / "lib" / "ascii",
        build_dir / "src",
        dirs_exist_ok=True,
    )

    shutil.copytree(
        source_dir / "lib" / "terminal",
        build_dir / "src",
        dirs_exist_ok=True,
    )

    shutil.copytree(
        source_dir / "main",
        build_dir / "src",
        dirs_exist_ok=True,
    )

    shutil.copytree(
        source_dir / "instruction" / "template",
        build_dir / "src",
        dirs_exist_ok=True,
    )

    shutil.copytree(
        source_dir / "instruction" / "function",
        build_dir / "src",
        dirs_exist_ok=True,
    )

    # Copy debug sources
    shutil.copytree(source_dir / "test", build_dir / "src", dirs_exist_ok=True)

    # Copy config
    shutil.copy(config, build_dir / MCB_CONFIG_FILE)

    # Create dummy pack.mcmeta
    with open(build_dir / "pack.mcmeta", "w") as f:
        meta = {"pack": {"pack_format": ctx.data.pack_format}}
        json.dump(meta, f)

    # Run mcb
    command = ["mcb", "build"]
    try:
        app = subprocess.run(
            command,
            cwd=build_dir,
            check=True,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            encoding="utf-8",
        )
        if app.returncode != 0 or "Error" in app.stdout or "Error" in app.stderr:
            raise subprocess.CalledProcessError(
                app.returncode, command, app.stdout, app.stderr
            )

    except subprocess.CalledProcessError as e:
        print(f"Error while running MCB: {e.stderr}")
        raise e

    # Load the built datapack
    ctx.data.load(build_dir)

    # Update source hash
    ctx.cache["mcbuild"].json["source_hash"] = source_hash
