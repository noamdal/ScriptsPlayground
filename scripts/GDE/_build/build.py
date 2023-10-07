#!/usr/bin/env python3
# coding=utf-8
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
import os
import sys
import subprocess
import hashlib
import shutil

pj = os.path.join
pn = os.path.normpath

script_path = os.path.dirname(os.path.realpath(__file__))
main_path = pn(pj(script_path, "..", "GDE"))
ingredients_path = pn(pj(main_path, "ingredients"))

if sys.argv[1] == "ui":
    os.chdir(ingredients_path)
    print("Converting UI files to python...")
    about_ui = subprocess.run(["uic", "about.ui", "-o", "about_ui.py", "-tr", "translateGDE", "--idbased", "-g=python"], check=False, capture_output=True,     text=True)
    print(about_ui.stdout)
    main_ui = subprocess.run(["uic", "GDE.ui", "-o", "GDE_ui.py", "-tr", "translateGDE", "--idbased", "-g=python"], check=False, capture_output=True, text=True)
    print(main_ui.stdout)
    group_selection_ui = subprocess.run(["uic", "group_selection.ui", "-o", "group_selection_ui.py", "-tr", "translateGDE", "--idbased", "-g=python"],     check=False, capture_output=True, text=True)
    print(group_selection_ui.stdout)
elif sys.argv[1] == "tr":
    print("Updating translation files")
    os.chdir(main_path)
    import importlib.util
    spec = importlib.util.spec_from_file_location("GDE", pj(main_path, "GDE.py"))
    GDE = importlib.util.module_from_spec(spec)
    sys.modules["GDE"] = GDE
    spec.loader.exec_module(GDE)
    translation_tool = subprocess.run(["xgettext", pn("./GDE.py"), pn("./ingredients/about_ui.py"), pn("./ingredients/GDE_ui.py"), pn("./ingredients/group_selection_ui.py"), "-o", pj(main_path, "locales", "GDE.pot"), "--keyword=translateGDE", "--package-name", "Groups Domains Extractor", "--copyright-holder", "Filters Heroes", "--package-version", GDE.version()], check=False, capture_output=True, text=True)
    print(translation_tool.stdout)
elif sys.argv[1] == "package":
    main_path = pn(pj(script_path, ".."))
    dirs_needs_cleaned = [
        pj(main_path, "build"),
        pj(main_path, "dist"),
        pj(main_path, "GDE.egg-info")
    ]
    for dir_needs_cleaned in dirs_needs_cleaned:
        if os.path.exists(dir_needs_cleaned):
            shutil.rmtree(dir_needs_cleaned)
    os.chdir(main_path)
    print("Packaging...")
    build_tool = subprocess.run(["python", "-m", "build"], check=False, capture_output=True, text=True)
    print(build_tool.stdout)
    print(build_tool.stderr)
    print("Creating installer for Windows...")
    pynsist = subprocess.run(["pynsist", "pynsist.cfg"], check=False, capture_output=True, text=True)
    print(pynsist.stdout)
    print(pynsist.stderr)
    import importlib.util
    spec = importlib.util.spec_from_file_location("GDE", pj(main_path, "GDE", "GDE.py"))
    GDE = importlib.util.module_from_spec(spec)
    sys.modules["GDE"] = GDE
    spec.loader.exec_module(GDE)
    GDE_version = GDE.version()
    shutil.copy2(pj(main_path, "build", "nsis", f"GDE_{GDE_version}.exe"), pj(main_path, "dist"))
    print("Creating checksums...")
    dist_files = [
        pj(main_path, "dist", f"GDE-{GDE_version}.tar.gz"),
        pj(main_path, "dist", f"GDE-{GDE_version}-py3-none-any.whl"),
        pj(main_path, "dist", f"GDE_{GDE_version}.exe"),
    ]
    for dist_file in dist_files:
        if os.path.exists(dist_file):
            with open(dist_file, 'rb') as file_to_check:
                data = file_to_check.read()
            checksum_ext = hashlib.sha256(data).hexdigest()
            checksum_file_path = pj("dist", f"GDE-{GDE_version}.sha256")
            with open(checksum_file_path, "a", encoding='utf-8') as checksum_file:
                checksum_file.write(
                    checksum_ext+" "+os.path.basename(dist_file)+"\n")
