from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.database import db, Announcement, StudyGroup, Registration

# ===========================
# Blueprint Setup
# ===========================
admin_bp = Blueprint(
    "admin",
    __name__,
    url_prefix="/admin"
)


# ===========================
# Admin Dashboard
# ===========================
@admin_bp.route("/")
def dashboard():
    """Main admin panel overview page."""
    announcements_count = Announcement.query.count()
    groups_count        = StudyGroup.query.count()
    registrations_count = Registration.query.count()
    pending_count       = Registration.query.filter_by(
                              status=Registration.STATUS_PENDING
                          ).count()

    return render_template(
        "admin/dashboard.html",
        announcements_count=announcements_count,
        groups_count=groups_count,
        registrations_count=registrations_count,
        pending_count=pending_count,
    )


# ===================================================
# ANNOUNCEMENTS — Create / List / Delete
# ===================================================
@admin_bp.route("/announcements")
def announcements():
    """List all announcements."""
    all_announcements = Announcement.query.order_by(
        Announcement.published_at.desc()
    ).all()
    return render_template(
        "admin/announcements.html",
        announcements=all_announcements
    )


@admin_bp.route("/announcements/create", methods=["GET", "POST"])
def create_announcement():
    """Show creation form (GET) and handle submission (POST)."""
    if request.method == "POST":
        title   = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()

        # --- Validation ---
        if not title or not content:
            flash("Please fill in both the title and the content.", "danger")
            return render_template("admin/announcement_form.html",
                                   form_data=request.form)

        new_announcement = Announcement(title=title, content=content)
        db.session.add(new_announcement)
        db.session.commit()

        flash(f'Announcement "{title}" has been created successfully.', "success")
        return redirect(url_for("admin.announcements"))

    return render_template("admin/announcement_form.html", form_data={})


@admin_bp.route("/announcements/delete/<int:announcement_id>",
                methods=["POST"])
def delete_announcement(announcement_id):
    """Delete an announcement by ID."""
    announcement = Announcement.query.get_or_404(announcement_id)
    db.session.delete(announcement)
    db.session.commit()

    flash(f'Announcement "{announcement.title}" has been deleted.', "warning")
    return redirect(url_for("admin.announcements"))


# ===================================================
# STUDY GROUPS — Create / List / Delete
# ===================================================
@admin_bp.route("/groups")
def groups():
    """List all study groups."""
    all_groups = StudyGroup.query.order_by(StudyGroup.level).all()
    return render_template("admin/groups.html", groups=all_groups)


@admin_bp.route("/groups/create", methods=["GET", "POST"])
def create_group():
    """Show creation form (GET) and handle submission (POST)."""
    if request.method == "POST":
        level           = request.form.get("level", "").strip()
        schedule        = request.form.get("schedule", "").strip()
        available_spots = request.form.get("available_spots", "").strip()

        # --- Validation ---
        errors = []
        if not level:
            errors.append("Level name is required.")
        if not schedule:
            errors.append("Schedule is required.")
        if not available_spots.isdigit() or int(available_spots) < 1:
            errors.append("Available spots must be a positive number.")

        if errors:
            for error in errors:
                flash(error, "danger")
            return render_template("admin/group_form.html",
                                   form_data=request.form)

        new_group = StudyGroup(
            level=level,
            schedule=schedule,
            available_spots=int(available_spots),
        )
        db.session.add(new_group)
        db.session.commit()

        flash(f'Group "{level}" has been created successfully.', "success")
        return redirect(url_for("admin.groups"))

    return render_template("admin/group_form.html", form_data={})


@admin_bp.route("/groups/delete/<int:group_id>", methods=["POST"])
def delete_group(group_id):
    """
    Delete a study group by ID.
    Also removes all registrations linked to this group.
    """
    group = StudyGroup.query.get_or_404(group_id)

    # Remove linked registrations first to avoid FK constraint errors
    Registration.query.filter_by(group_id=group.id).delete()

    db.session.delete(group)
    db.session.commit()

    flash(f'Group "{group.level}" and all its registrations have been deleted.',
          "warning")
    return redirect(url_for("admin.groups"))


# ===================================================
# REGISTRATIONS — View / Update Status / Delete
# ===================================================
@admin_bp.route("/registrations")
def registrations():
    """
    List all student registrations.
    Supports optional filtering by status via ?status=pending etc.
    """
    status_filter = request.args.get("status", "all")

    query = Registration.query.join(StudyGroup).order_by(
        Registration.created_at.desc()
    )

    if status_filter in Registration.ALLOWED_STATUSES:
        query = query.filter(Registration.status == status_filter)

    all_registrations = query.all()

    return render_template(
        "admin/registrations.html",
        registrations=all_registrations,
        status_filter=status_filter,
        allowed_statuses=Registration.ALLOWED_STATUSES,
    )


@admin_bp.route("/registrations/update/<int:reg_id>", methods=["POST"])
def update_registration_status(reg_id):
    """Approve or reject a student registration."""
    registration = Registration.query.get_or_404(reg_id)
    new_status   = request.form.get("status", "").strip()

    if new_status not in Registration.ALLOWED_STATUSES:
        flash("Invalid status value.", "danger")
        return redirect(url_for("admin.registrations"))

    # If approving, check that spots are still available
    if new_status == Registration.STATUS_APPROVED:
        group = StudyGroup.query.get(registration.group_id)
        if group.available_spots < 1:
            flash(
                f'No available spots left in "{group.level}". '
                f'Cannot approve this registration.',
                "danger"
            )
            return redirect(url_for("admin.registrations"))

        # Decrement available spots
        group.available_spots -= 1

    # If previously approved and now being rejected — restore the spot
    if (registration.status == Registration.STATUS_APPROVED and
            new_status == Registration.STATUS_REJECTED):
        group = StudyGroup.query.get(registration.group_id)
        group.available_spots += 1

    registration.status = new_status
    db.session.commit()

    flash(
        f'Registration for "{registration.student_name}" '
        f'updated to "{new_status}".',
        "success"
    )
    return redirect(url_for("admin.registrations"))


@admin_bp.route("/registrations/delete/<int:reg_id>", methods=["POST"])
def delete_registration(reg_id):
    """Delete a single registration record."""
    registration = Registration.query.get_or_404(reg_id)

    # Restore spot if the registration was approved
    if registration.status == Registration.STATUS_APPROVED:
        group = StudyGroup.query.get(registration.group_id)
        if group:
            group.available_spots += 1

    db.session.delete(registration)
    db.session.commit()

    flash(
        f'Registration for "{registration.student_name}" has been deleted.',
        "warning"
    )
    return redirect(url_for("admin.registrations"))