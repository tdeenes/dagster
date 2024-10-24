from dagster._core.libraries import DagsterLibraryRegistry

from dagster_tableau.assets import (
    build_tableau_executable_assets_definition as build_tableau_executable_assets_definition,
)
from dagster_tableau.resources import (
    TableauCloudWorkspace as TableauCloudWorkspace,
    TableauServerWorkspace as TableauServerWorkspace,
    load_tableau_asset_specs as load_tableau_asset_specs,
)
from dagster_tableau.translator import DagsterTableauTranslator as DagsterTableauTranslator
from dagster_tableau.version import __version__ as __version__

DagsterLibraryRegistry.register("dagster-tableau", __version__)
