from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.database import db, Announcement, StudyGroup, Registration

# ===========================
# Blueprint Setup
# ===========================
main_bp = Blueprint(
    "main",
    __name__,
    url_prefix="/"
)


# ===========================
# Home Page
# ===========================
@main_bp.route("/")
def index():
    """
    Main public page.
    Displays:
      - Latest announcements in reverse chronological order
      - All study groups that still have available spots
    """
    announcements = Announcement.query.order_by(
        Announcement.published_at.desc()
    ).all()

    available_groups = StudyGroup.query.filter(
        StudyGroup.available_spots > 0
    ).order_by(StudyGroup.level).all()

    return render_template(
        "index.html",
        announcements=announcements,
        available_groups=available_groups,
    )


# ===========================
# Registration Form
# ===========================
@main_bp.route("/register", methods=["GET", "POST"])
def register():
    """
    Student registration page.
    GET  — show the sign-up form with a list of available groups.
    POST — validate and save the new registration.
    """
    available_groups = StudyGroup.query.filter(
        StudyGroup.available_spots > 0
    ).order_by(StudyGroup.level).all()

    if request.method == "POST":
        student_name = request.form.get("student_name", "").strip()
        phone        = request.form.get("phone", "").strip()
        group_id     = request.form.get("group_id", "").strip()

        # --- Validation ---
        errors = []

        if not student_name:
            errors.append("Please enter your full name.")

        if not phone:
            errors.append("Please enter your phone number.")

        if not group_id or not group_id.isdigit():
            errors.append("Please select a valid study group.")

        if errors:
            for error in errors:
                flash(error, "danger")
            return render_template(
                "register.html",
                available_groups=available_groups,
                form_data=request.form,
            )

        # --- Check group still exists and has spots ---
        group = StudyGroup.query.get(int(group_id))

        if not group:
            flash("The selected group does not exist. Please try again.", "danger")
            return render_template(
                "register.html",
                available_groups=available_groups,
                form_data=request.form,
            )

        if group.available_spots < 1:
            flash(
                f'Sorry, the group "{group.level}" is now full. '
                f'Please choose another group.',
                "warning"
            )
            return render_template(
                "register.html",
                available_groups=available_groups,
                form_data=request.form,
            )

        # --- Check for duplicate registration ---
        existing = Registration.query.filter_by(
            phone=phone,
            group_id=group.id
        ).first()

        if existing:
            flash(
                "A registration with this phone number already exists "
                "for the selected group.",
                "warning"
            )
            return render_template(
                "register.html",
                available_groups=available_groups,
                form_data=request.form,
            )

        # --- Save registration ---
        new_registration = Registration(
            student_name=student_name,
            phone=phone,
            group_id=group.id,
            status=Registration.STATUS_PENDING,
        )
        db.session.add(new_registration)
        db.session.commit()

        flash(
            f'Thank you, {student_name}! Your application for '
            f'"{group.level}" has been received. '
            f'We will contact you shortly.',
            "success"
        )
        return redirect(url_for("main.success"))

    return render_template(
        "register.html",
        available_groups=available_groups,
        form_data={},
    )


# ===========================
# Success Page
# ===========================
@main_bp.route("/success")
def success():
    """
    Confirmation page shown after a successful registration submission.
    """
    return render_template("success.html")


# ===========================
# Announcements Archive
# ===========================
@main_bp.route("/announcements")
def announcements():
    """
    Full paginated list of all announcements.
    Supports ?page=N query parameter (10 per page).
    """
    page = request.args.get("page", 1, type=int)
    per_page = 10

    pagination = Announcement.query.order_by(
        Announcement.published_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)

    return render_template(
        "announcements.html",
        announcements=pagination.items,
        pagination=pagination,
    )


# ===========================
# Single Announcement Detail
# ===========================
@main_bp.route("/announcements/<int:announcement_id>")
def announcement_detail(announcement_id):
    """
    Detail view for a single announcement.
    Returns 404 if not found.
    """
    announcement = Announcement.query.get_or_404(announcement_id)
    return render_template("announcement_detail.html",
                           announcement=announcement)


# ===========================
# All Groups Page
# ===========================
@main_bp.route("/groups")
def groups():
    """
    Public page listing all study groups,
    including those that are currently full.
    """
    all_groups = StudyGroup.query.order_by(StudyGroup.level).all()
    return render_template("groups.html", groups=all_groups)

