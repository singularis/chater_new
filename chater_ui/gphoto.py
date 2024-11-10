import logging
import os
from datetime import date

from flask import flash, redirect, render_template, request, url_for

log = logging.getLogger("main")


def gphoto(session, pic_folder):
    if "logged_in" in session:
        if request.method == "GET":
            media = {}
            years = os.listdir(pic_folder)
            logging.info(f"years {years}")
            for year in years:
                media_folder = os.path.join(pic_folder, str(year))
                file_list = os.listdir(media_folder)
                year_media = {"images": [], "videos": []}
                for file in file_list:
                    if file.lower().endswith(
                        (".png", ".jpg", ".jpeg", ".gif", ".heic")
                    ):
                        year_media["images"].append(
                            os.path.join("pics", str(year), file)
                        )
                    elif file.lower().endswith((".mp4", ".mov", ".avi")):
                        year_media["videos"].append(
                            os.path.join("pics", str(year), file)
                        )
                media[int(year)] = year_media
            return render_template(
                "gphoto.html",
                years=[int(x) for x in years],
                media=media,
                date=date.today(),
            )
    else:
        logging.warning("Unauthorized chater access attempt")
        flash("You need to log in to view this page")
        return redirect(url_for("chater_login"))
