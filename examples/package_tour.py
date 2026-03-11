from tscfbench.product import (
    render_api_handbook_markdown,
    render_cli_guide_markdown,
    render_environment_profiles_markdown,
    render_package_overview_markdown,
    render_use_cases_markdown,
)

print(render_package_overview_markdown())
print("
" + "=" * 80 + "
")
print(render_api_handbook_markdown())
print("
" + "=" * 80 + "
")
print(render_use_cases_markdown())
print("
" + "=" * 80 + "
")
print(render_environment_profiles_markdown())
print("
" + "=" * 80 + "
")
print(render_cli_guide_markdown())
