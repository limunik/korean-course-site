from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.database import db, Announcement, StudyGroup, Registration

# ===========================
# Blueprint Setup
# ===========================
admin_bp = Blueprint(
    "admin",
    __name__,
    url_prefix="/admin-secret"        # ← secret URL, not /admin
)


# ===========================
# Dashboard / Announcements
# ===========================
@admin_bp.route("/")
def dashboard():
    """
    Main admin page.
    Shows the announcement creation form + list of all announcements.
    """
    announcements = Announcement.query.order_by(
        Announcement.published_at.desc()
    ).all()

    pending_count = Registration.query.filter_by(
        status=Registration.STATUS_PENDING
    ).count()

    groups_count = StudyGroup.query.count()

    return render_template(
        "admin.html",
        announcements=announcements,
        pending_count=pending_count,
        groups_count=groups_count,
    )


# ===========================
# Create Announcement — POST
# ===========================
@admin_bp.route("/announcements/create", methods=["POST"])
def create_announcement():
    """
    Handles the New Announcement form submission.
    Validates input, saves to DB, flashes result, redirects back.
    """
    title   = request.form.get("title",   "").strip()
    content = request.form.get("content", "").strip()

    # ── Validation ──────────────────────────────────────────
    errors = []

    if not title:
        errors.append("Заголовок не может быть пустым.")
    elif len(title) > 200:
        errors.append("Заголовок слишком длинный (максимум 200 символов).")

    if not content:
        errors.append("Текст объявления не может быть пустым.")

    if errors:
        for error in errors:
            flash(error, "danger")
        return redirect(url_for("admin.dashboard"))

    # ── Save to database ─────────────────────────────────────
    new_announcement = Announcement(title=title, content=content)
    db.session.add(new_announcement)
    db.session.commit()

    flash(f'✅ Объявление «{title}» успешно опубликовано.', "success")
    return redirect(url_for("admin.dashboard"))


# ===========================
# Delete Announcement — POST
# ===========================
@admin_bp.route("/announcements/delete/<int:announcement_id>", methods=["POST"])
def delete_announcement(announcement_id):
    """
    Deletes a single announcement by ID.
    Returns 404 if not found.
    """
    announcement = Announcement.query.get_or_404(announcement_id)
    title = announcement.title

    db.session.delete(announcement)
    db.session.commit()

    flash(f'🗑️ Объявление «{title}» удалено.', "warning")
    return redirect(url_for("admin.dashboard"))


# ===========================
# Registrations List
# ===========================
@admin_bp.route("/registrations")
def registrations():
    """
    Shows all student registrations.
    Optional ?status= filter: pending / approved / rejected
    """
    status_filter = request.args.get("status", "all")

    query = Registration.query.join(StudyGroup).order_by(
        Registration.created_at.desc()
    )

    if status_filter in Registration.ALLOWED_STATUSES:
        query = query.filter(Registration.status == status_filter)

    all_registrations = query.all()

    pending_count = Registration.query.filter_by(
        status=Registration.STATUS_PENDING
    ).count()

    return render_template(
        "admin_registrations.html",
        registrations=all_registrations,
        status_filter=status_filter,
        allowed_statuses=Registration.ALLOWED_STATUSES,
        pending_count=pending_count,
        groups_count=StudyGroup.query.count(),
    )


# ===========================
# Update Registration Status
# ===========================
@admin_bp.route("/registrations/update/<int:reg_id>", methods=["POST"])
def update_registration_status(reg_id):
    """Approve or reject a student registration."""
    registration = Registration.query.get_or_404(reg_id)
    new_status   = request.form.get("status", "").strip()

    if new_status not in Registration.ALLOWED_STATUSES:
        flash("Недопустимый статус.", "danger")
        return redirect(url_for("admin.registrations"))

    # Approving — check spots available
    if new_status == Registration.STATUS_APPROVED:
        group = StudyGroup.query.get(registration.group_id)
        if group.available_spots < 1:
            flash(
                f'В группе «{group.level}» нет свободных мест.',
                "danger"
            )
            return redirect(url_for("admin.registrations"))
        group.available_spots -= 1

    # Rejecting a previously approved record — restore the spot
    if (registration.status == Registration.STATUS_APPROVED and
            new_status == Registration.STATUS_REJECTED):
        group = StudyGroup.query.get(registration.group_id)
        if group:
            group.available_spots += 1

    registration.status = new_status
    db.session.commit()

    flash(
        f'Статус заявки «{registration.student_name}» обновлён на «{new_status}».',
        "success"
    )
    return redirect(url_for("admin.registrations"))


# ===========================
# Groups Management
# ===========================
@admin_bp.route("/groups")
def groups():
    """Lists all study groups."""
    all_groups = StudyGroup.query.order_by(StudyGroup.level).all()

    pending_count = Registration.query.filter_by(
        status=Registration.STATUS_PENDING
    ).count()

    return render_template(
        "admin_groups.html",
        groups=all_groups,
        pending_count=pending_count,
        groups_count=len(all_groups),
    )


@admin_bp.route("/groups/create", methods=["POST"])
def create_group():
    """Creates a new study group."""
    level           = request.form.get("level",           "").strip()
    schedule        = request.form.get("schedule",        "").strip()
    available_spots = request.form.get("available_spots", "").strip()

    errors = []
    if not level:
        errors.append("Название уровня обязательно.")
    if not schedule:
        errors.append("Расписание обязательно.")
    if not available_spots.isdigit() or int(available_spots) < 1:
        errors.append("Количество мест должно быть положительным числом.")

    if errors:
        for error in errors:
            flash(error, "danger")
        return redirect(url_for("admin.groups"))

    new_group = StudyGroup(
        level=level,
        schedule=schedule,
        available_spots=int(available_spots),
    )
    db.session.add(new_group)
    db.session.commit()

    flash(f'✅ Группа «{level}» создана.', "success")
    return redirect(url_for("admin.groups"))


@admin_bp.route("/groups/delete/<int:group_id>", methods=["POST"])
def delete_group(group_id):
    """Deletes a group and all its linked registrations."""
    group = StudyGroup.query.get_or_404(group_id)
    Registration.query.filter_by(group_id=group.id).delete()
    db.session.delete(group)
    db.session.commit()

    flash(f'🗑️ Группа «{group.level}» и все её заявки удалены.', "warning")
    return redirect(url_for("admin.groups"))