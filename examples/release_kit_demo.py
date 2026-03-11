"""Example: generate a release-facing markdown kit."""

from tscfbench.narrative import write_release_kit


def main() -> None:
    manifest = write_release_kit("release_kit_demo")
    print(manifest)


if __name__ == "__main__":
    main()
