import os
import textwrap
from pathlib import Path

from dagster._utils.env import environ
from docs_beta_snippets_tests.snippet_checks.guides.components.utils import (
    DAGSTER_ROOT,
    EDITABLE_DIR,
    MASK_EDITABLE_DAGSTER,
    MASK_JAFFLE_PLATFORM,
    MASK_SLING_DOWNLOAD_DUCKDB,
    MASK_SLING_PROMO,
    MASK_SLING_WARNING,
    MASK_TIME,
    format_multiline,
    isolated_snippet_generation_environment,
)
from docs_beta_snippets_tests.snippet_checks.utils import (
    _run_command,
    check_file,
    compare_tree_output,
    create_file,
    re_ignore_after,
    re_ignore_before,
    run_command_and_snippet_output,
)

COMPONENTS_SNIPPETS_DIR = (
    DAGSTER_ROOT
    / "examples"
    / "docs_beta_snippets"
    / "docs_beta_snippets"
    / "guides"
    / "components"
    / "index"
)


def test_components_docs_index(update_snippets: bool) -> None:
    snip_no = 0

    def next_snip_no():
        nonlocal snip_no
        snip_no += 1
        return snip_no

    with isolated_snippet_generation_environment():
        run_command_and_snippet_output(
            cmd="dg --help",
            snippet_path=COMPONENTS_SNIPPETS_DIR / f"{next_snip_no()}-help.txt",
            update_snippets=update_snippets,
        )

        # Scaffold project
        run_command_and_snippet_output(
            cmd="dg scaffold project jaffle-platform --use-editable-dagster",
            snippet_path=COMPONENTS_SNIPPETS_DIR / f"{next_snip_no()}-scaffold.txt",
            update_snippets=update_snippets,
            snippet_replace_regex=[
                MASK_EDITABLE_DAGSTER,
                MASK_JAFFLE_PLATFORM,
                (r"\nUsing[\s\S]*", "\n..."),
            ],
        )

        # Validate scaffolded files
        _run_command(r"find . -type d -name __pycache__ -exec rm -r {} \+")
        run_command_and_snippet_output(
            cmd="cd jaffle-platform && tree",
            snippet_path=COMPONENTS_SNIPPETS_DIR / f"{next_snip_no()}-tree.txt",
            update_snippets=update_snippets,
            custom_comparison_fn=compare_tree_output,
        )
        check_file(
            "pyproject.toml",
            COMPONENTS_SNIPPETS_DIR / f"{next_snip_no()}-pyproject.toml",
            update_snippets=update_snippets,
            snippet_replace_regex=[
                re_ignore_before("[tool.dagster]"),
                re_ignore_after('root_module = "jaffle_platform"'),
            ],
        )
        check_file(
            Path("jaffle_platform") / "definitions.py",
            COMPONENTS_SNIPPETS_DIR / f"{next_snip_no()}-definitions.py",
            update_snippets=update_snippets,
        )
        check_file(
            "pyproject.toml",
            COMPONENTS_SNIPPETS_DIR / f"{next_snip_no()}-pyproject.toml",
            update_snippets=update_snippets,
            snippet_replace_regex=[
                re_ignore_before("[project.entry-points]"),
                re_ignore_after(
                    '"dagster.components" = { jaffle_platform = "jaffle_platform.lib"}'
                ),
            ],
        )

        run_command_and_snippet_output(
            cmd="dg list component-type",
            snippet_path=COMPONENTS_SNIPPETS_DIR
            / f"{next_snip_no()}-dg-list-component-types.txt",
            update_snippets=update_snippets,
            snippet_replace_regex=[MASK_JAFFLE_PLATFORM],
        )

        _run_command(
            f"uv add sling_mac_arm64 && uv add --editable '{EDITABLE_DIR / 'dagster-sling'!s}' && uv add --editable '{EDITABLE_DIR / 'dagster-components'!s}[sling]'"
        )
        _run_command("uv tree")
        run_command_and_snippet_output(
            cmd="dg list component-type",
            snippet_path=COMPONENTS_SNIPPETS_DIR
            / f"{next_snip_no()}-dg-list-component-types.txt",
            update_snippets=update_snippets,
            snippet_replace_regex=[MASK_JAFFLE_PLATFORM],
        )

        # Scaffold new ingestion, validate new files
        run_command_and_snippet_output(
            cmd="dg scaffold component 'dagster_components.dagster_sling.SlingReplicationCollectionComponent' ingest_files",
            snippet_path=COMPONENTS_SNIPPETS_DIR
            / f"{next_snip_no()}-dg-scaffold-sling-replication.txt",
            update_snippets=update_snippets,
            snippet_replace_regex=[MASK_JAFFLE_PLATFORM],
        )
        # Cleanup __pycache__ directories
        _run_command(r"find . -type d -name __pycache__ -exec rm -r {} \+")
        run_command_and_snippet_output(
            cmd="tree jaffle_platform",
            snippet_path=COMPONENTS_SNIPPETS_DIR
            / f"{next_snip_no()}-tree-jaffle-platform.txt",
            update_snippets=update_snippets,
            custom_comparison_fn=compare_tree_output,
        )
        check_file(
            Path("jaffle_platform") / "defs" / "ingest_files" / "component.yaml",
            COMPONENTS_SNIPPETS_DIR / f"{next_snip_no()}-component.yaml",
            update_snippets=update_snippets,
        )

        # Set up duckdb Sling connection
        with environ(
            {
                "BUILDKITE_MESSAGE": ""
            }  # keep buildkite message from messing up sling parsing
        ):
            run_command_and_snippet_output(
                cmd="uv run sling conns set DUCKDB type=duckdb instance=/tmp/jaffle_platform.duckdb",
                snippet_path=COMPONENTS_SNIPPETS_DIR
                / f"{next_snip_no()}-sling-setup-duckdb.txt",
                update_snippets=update_snippets,
                snippet_replace_regex=[
                    MASK_SLING_WARNING,
                    MASK_SLING_PROMO,
                    MASK_TIME,
                    (r"set in .*?.sling", "set in /.../.sling"),
                ],
            )
            run_command_and_snippet_output(
                cmd="uv run sling conns test DUCKDB",
                snippet_path=COMPONENTS_SNIPPETS_DIR
                / f"{next_snip_no()}-sling-test-duckdb.txt",
                update_snippets=update_snippets,
                snippet_replace_regex=[
                    MASK_SLING_WARNING,
                    MASK_SLING_DOWNLOAD_DUCKDB,
                    MASK_SLING_PROMO,
                    MASK_TIME,
                ],
            )

        sling_duckdb_path = Path("/") / "tmp" / ".sling" / "bin" / "duckdb"
        sling_duckdb_version = next(iter(os.listdir()), None)
        with environ(
            {
                "PATH": f'{os.environ["PATH"]}:{sling_duckdb_path / sling_duckdb_version!s}'
            }
            if sling_duckdb_version
            else {}
        ):
            # Test sling sync
            run_command_and_snippet_output(
                cmd=textwrap.dedent("""
                    curl -O https://raw.githubusercontent.com/dbt-labs/jaffle-shop-classic/refs/heads/main/seeds/raw_customers.csv &&
                    curl -O https://raw.githubusercontent.com/dbt-labs/jaffle-shop-classic/refs/heads/main/seeds/raw_orders.csv &&
                    curl -O https://raw.githubusercontent.com/dbt-labs/jaffle-shop-classic/refs/heads/main/seeds/raw_payments.csv
                """).strip(),
                snippet_path=COMPONENTS_SNIPPETS_DIR / f"{next_snip_no()}-curl.txt",
                update_snippets=update_snippets,
                ignore_output=True,
            )
            create_file(
                file_path=Path("jaffle_platform")
                / "defs"
                / "ingest_files"
                / "replication.yaml",
                snippet_path=COMPONENTS_SNIPPETS_DIR
                / f"{next_snip_no()}-replication.yaml",
                contents=textwrap.dedent(
                    """
                    source: LOCAL
                    target: DUCKDB

                    defaults:
                      mode: full-refresh
                      object: "{stream_table}"

                    streams:
                      file://raw_customers.csv:
                        object: "main.raw_customers"
                      file://raw_orders.csv:
                        object: "main.raw_orders"
                      file://raw_payments.csv:
                        object: "main.raw_payments"
                """,
                ).strip(),
            )
            _run_command(
                "uv run dagster asset materialize --select '*' -m jaffle_platform.definitions"
            )
            run_command_and_snippet_output(
                cmd='duckdb /tmp/jaffle_platform.duckdb -c "SELECT * FROM raw_customers LIMIT 5;"',
                snippet_path=COMPONENTS_SNIPPETS_DIR
                / f"{next_snip_no()}-duckdb-select.txt",
                update_snippets=update_snippets,
                snippet_replace_regex=[
                    (r"\d\d\d\d\d\d\d\d\d\d │\n", "...        | \n"),
                ],
            )

            # Set up dbt
            run_command_and_snippet_output(
                cmd="git clone --depth=1 https://github.com/dagster-io/jaffle-platform.git dbt && rm -rf dbt/.git",
                snippet_path=COMPONENTS_SNIPPETS_DIR
                / f"{next_snip_no()}-jaffle-clone.txt",
                update_snippets=update_snippets,
                ignore_output=True,
            )
            _run_command(
                f"uv add --editable '{EDITABLE_DIR / 'dagster-dbt'!s}' && uv add --editable '{EDITABLE_DIR / 'dagster-components'!s}[dbt]'; uv add dbt-duckdb"
            )
            run_command_and_snippet_output(
                cmd="dg list component-type",
                snippet_path=COMPONENTS_SNIPPETS_DIR
                / f"{next_snip_no()}-dg-list-component-types.txt",
                update_snippets=update_snippets,
                snippet_replace_regex=[MASK_JAFFLE_PLATFORM],
            )

            # Scaffold dbt project components
            run_command_and_snippet_output(
                cmd="dg scaffold component dagster_components.dagster_dbt.DbtProjectComponent jdbt --project-path dbt/jdbt",
                snippet_path=COMPONENTS_SNIPPETS_DIR
                / f"{next_snip_no()}-dg-scaffold-jdbt.txt",
                update_snippets=update_snippets,
                snippet_replace_regex=[MASK_JAFFLE_PLATFORM],
            )
            check_file(
                Path("jaffle_platform") / "defs" / "jdbt" / "component.yaml",
                COMPONENTS_SNIPPETS_DIR / f"{next_snip_no()}-component-jdbt.yaml",
                update_snippets=update_snippets,
            )

            # Update component file, with error, check and fix
            create_file(
                Path("jaffle_platform") / "defs" / "jdbt" / "component.yaml",
                snippet_path=COMPONENTS_SNIPPETS_DIR
                / f"{next_snip_no()}-project-jdbt-incorrect.yaml",
                contents=format_multiline("""
                    type: dagster_components.dbt_project

                    attributes:
                      dbt:
                        project_dir: ../../../dbt/jdbt
                      asset_attributes:
                        key: "target/main/{{ node.name }}
                """),
            )
            run_command_and_snippet_output(
                cmd="dg check yaml",
                snippet_path=COMPONENTS_SNIPPETS_DIR
                / f"{next_snip_no()}-dg-component-check-error.txt",
                update_snippets=update_snippets,
                snippet_replace_regex=[
                    MASK_JAFFLE_PLATFORM,
                ],
                expect_error=True,
            )

            create_file(
                Path("jaffle_platform") / "defs" / "jdbt" / "component.yaml",
                snippet_path=COMPONENTS_SNIPPETS_DIR
                / f"{next_snip_no()}-project-jdbt.yaml",
                contents=format_multiline("""
                    type: dagster_components.dagster_dbt.DbtProjectComponent

                    attributes:
                      dbt:
                        project_dir: ../../../dbt/jdbt
                      asset_attributes:
                        key: "target/main/{{ node.name }}"
                """),
            )
            run_command_and_snippet_output(
                cmd="dg check yaml",
                snippet_path=COMPONENTS_SNIPPETS_DIR
                / f"{next_snip_no()}-dg-component-check.txt",
                update_snippets=update_snippets,
                snippet_replace_regex=[
                    MASK_JAFFLE_PLATFORM,
                ],
            )

            # Run dbt, check works
            _run_command(
                "DAGSTER_IS_DEV_CLI=1 uv run dagster asset materialize --select '*' -m jaffle_platform.definitions"
            )
            run_command_and_snippet_output(
                cmd='duckdb /tmp/jaffle_platform.duckdb -c "SELECT * FROM orders LIMIT 5;"',
                snippet_path=COMPONENTS_SNIPPETS_DIR
                / f"{next_snip_no()}-duckdb-select-orders.txt",
                update_snippets=update_snippets,
            )
