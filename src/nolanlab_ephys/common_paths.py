"""
File containing useful paths that you might use in your project.
E.g. where the `ActiveProjects` on different machines such as your laptop, desktop and on EDDIE.
Can be a helpful place to store paths to data and derivative folders.
"""

from pathlib import Path

eddie_active_projects = Path(
    "/exports/cmvm/datastore/sbms/groups/CDBS_SIDB_storage/NolanLab/ActiveProjects/"
)

chris_desktop_active_projects = Path(
    "/run/user/1000/gvfs/smb-share:server=cmvm.datastore.ed.ac.uk,share=cmvm/sbms/groups/CDBS_SIDB_storage/NolanLab/ActiveProjects/"
)
chris_laptop_active_projects = Path(
    "/Volumes/cmvm/sbms/groups/CDBS_SIDB_storage/NolanLab/ActiveProjects"
)
