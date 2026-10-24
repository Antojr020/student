import matplotlib.pyplot as plt
import matplotlib.patches as patches

def create_architecture_diagram():
    fig, ax = plt.subplots(figsize=(8.5, 5.5), dpi=300)
    ax.axis('off')

    # Background color white
    fig.patch.set_facecolor('white')

    # Outer Container: Client Layer
    rect_client = patches.FancyBboxPatch((0.05, 0.65), 0.90, 0.30, boxstyle="round,pad=0.02,rounding_size=0.03",
                                         facecolor='#f8fafc', edgecolor='#0f172a', linewidth=1.5)
    ax.add_patch(rect_client)
    ax.text(0.08, 0.91, "Client Layer (Web Browser)", fontsize=11, fontweight='bold', color='#0f172a')

    # Sub-boxes in Client Layer
    box_portals = patches.FancyBboxPatch((0.08, 0.68), 0.26, 0.20, boxstyle="round,pad=0.01,rounding_size=0.02",
                                         facecolor='#ffffff', edgecolor='#334155', linewidth=1)
    ax.add_patch(box_portals)
    ax.text(0.21, 0.81, "Role-Based Portals", fontsize=9, fontweight='bold', ha='center', color='#1e3a8a')
    ax.text(0.21, 0.76, "• Admin & Staff Portals\n• Student & Parent Portals", fontsize=7.5, ha='center', color='#334155')

    box_ui = patches.FancyBboxPatch((0.37, 0.68), 0.26, 0.20, boxstyle="round,pad=0.01,rounding_size=0.02",
                                    facecolor='#ffffff', edgecolor='#334155', linewidth=1)
    ax.add_patch(box_ui)
    ax.text(0.50, 0.81, "Presentation UI (HTML/CSS)", fontsize=9, fontweight='bold', ha='center', color='#1e3a8a')
    ax.text(0.50, 0.76, "• Bootstrap 5.3 & Icons\n• Responsive Dark/Light", fontsize=7.5, ha='center', color='#334155')

    box_chart = patches.FancyBboxPatch((0.66, 0.68), 0.26, 0.20, boxstyle="round,pad=0.01,rounding_size=0.02",
                                      facecolor='#ffffff', edgecolor='#334155', linewidth=1)
    ax.add_patch(box_chart)
    ax.text(0.79, 0.81, "Client Interactivity", fontsize=9, fontweight='bold', ha='center', color='#1e3a8a')
    ax.text(0.79, 0.76, "• Chart.js Visualizer\n• Batch Table Calculations", fontsize=7.5, ha='center', color='#334155')

    # Outer Container: Server Layer
    rect_server = patches.FancyBboxPatch((0.05, 0.32), 0.90, 0.28, boxstyle="round,pad=0.02,rounding_size=0.03",
                                         facecolor='#f8fafc', edgecolor='#0f172a', linewidth=1.5)
    ax.add_patch(rect_server)
    ax.text(0.08, 0.56, "Application Server Layer (Python / Flask Framework)", fontsize=11, fontweight='bold', color='#0f172a')

    # Server components
    box_auth = patches.FancyBboxPatch((0.08, 0.35), 0.20, 0.18, boxstyle="round,pad=0.01,rounding_size=0.02",
                                      facecolor='#ffffff', edgecolor='#334155', linewidth=1)
    ax.add_patch(box_auth)
    ax.text(0.18, 0.46, "Authentication & RBAC", fontsize=8.5, fontweight='bold', ha='center', color='#1e3a8a')
    ax.text(0.18, 0.40, "• Flask-Login\n• Password Hashing", fontsize=7, ha='center', color='#334155')

    box_routes = patches.FancyBboxPatch((0.31, 0.35), 0.22, 0.18, boxstyle="round,pad=0.01,rounding_size=0.02",
                                        facecolor='#ffffff', edgecolor='#334155', linewidth=1)
    ax.add_patch(box_routes)
    ax.text(0.42, 0.46, "Core Academic Logic", fontsize=8.5, fontweight='bold', ha='center', color='#1e3a8a')
    ax.text(0.42, 0.40, "• Student & Faculty CRUD\n• Attendance Tracking", fontsize=7, ha='center', color='#334155')

    box_engine = patches.FancyBboxPatch((0.56, 0.35), 0.18, 0.18, boxstyle="round,pad=0.01,rounding_size=0.02",
                                        facecolor='#ffffff', edgecolor='#334155', linewidth=1)
    ax.add_patch(box_engine)
    ax.text(0.65, 0.46, "Evaluation Engine", fontsize=8.5, fontweight='bold', ha='center', color='#1e3a8a')
    ax.text(0.65, 0.40, "• SGPA / CGPA\n• 10-Point UGC Scale", fontsize=7, ha='center', color='#334155')

    box_pdf = patches.FancyBboxPatch((0.77, 0.35), 0.15, 0.18, boxstyle="round,pad=0.01,rounding_size=0.02",
                                     facecolor='#ffffff', edgecolor='#334155', linewidth=1)
    ax.add_patch(box_pdf)
    ax.text(0.845, 0.46, "ReportLab Engine", fontsize=8.5, fontweight='bold', ha='center', color='#1e3a8a')
    ax.text(0.845, 0.40, "• Official PDF Marksheet\n• Vector Rendering", fontsize=7, ha='center', color='#334155')

    # Outer Container: Data Persistence Layer
    rect_db = patches.FancyBboxPatch((0.05, 0.05), 0.90, 0.22, boxstyle="round,pad=0.02,rounding_size=0.03",
                                     facecolor='#f8fafc', edgecolor='#0f172a', linewidth=1.5)
    ax.add_patch(rect_db)
    ax.text(0.08, 0.23, "Data Persistence Layer (SQLAlchemy ORM / Relational Database)", fontsize=11, fontweight='bold', color='#0f172a')

    # Tables list
    db_items = [
        ("Users & Roles", 0.16),
        ("Students & Parents", 0.33),
        ("Faculty & Subjects", 0.50),
        ("Examinations & Marks", 0.67),
        ("Attendance & Audit Logs", 0.84)
    ]
    for title, x_center in db_items:
        tbl_box = patches.FancyBboxPatch((x_center - 0.075, 0.08), 0.15, 0.12, boxstyle="round,pad=0.01,rounding_size=0.02",
                                         facecolor='#ffffff', edgecolor='#334155', linewidth=1)
        ax.add_patch(tbl_box)
        ax.text(x_center, 0.14, title, fontsize=7.5, fontweight='bold', ha='center', color='#0f2b5c')

    # Arrows between layers
    arrow1 = patches.FancyArrowPatch((0.50, 0.65), (0.50, 0.60), arrowstyle='<->', mutation_scale=15, color='#0f172a', lw=1.5)
    ax.add_patch(arrow1)
    ax.text(0.53, 0.62, "HTTP / JSON REST", fontsize=7.5, color='#64748b')

    arrow2 = patches.FancyArrowPatch((0.50, 0.32), (0.50, 0.27), arrowstyle='<->', mutation_scale=15, color='#0f172a', lw=1.5)
    ax.add_patch(arrow2)
    ax.text(0.53, 0.29, "SQLAlchemy ORM Queries", fontsize=7.5, color='#64748b')

    plt.tight_layout()
    plt.savefig('report_assets/fig_2_1_architecture.png', bbox_inches='tight', dpi=300)
    plt.close()
    print("Created fig_2_1_architecture.png")


def create_workflow_diagram():
    fig, ax = plt.subplots(figsize=(8.5, 4.5), dpi=300)
    ax.axis('off')
    fig.patch.set_facecolor('white')

    # Workflow blocks
    steps = [
        ("Start\nFaculty Login", 0.08, 0.75, "start"),
        ("Select Subject &\nExamination", 0.25, 0.75, "process"),
        ("Enter Internal &\nExternal Scores", 0.44, 0.75, "process"),
        ("Valid Score\nBounds?", 0.64, 0.75, "decision"),
        ("Save as Draft\nor Submit", 0.84, 0.75, "process"),
        
        ("Admin Review &\nVerification", 0.84, 0.25, "process"),
        ("Approved by\nAuthority?", 0.64, 0.25, "decision"),
        ("Lock & Publish\nOfficial Results", 0.44, 0.25, "process"),
        ("Student Portal\nView & PDF Export", 0.25, 0.25, "process"),
        ("End\nPublished", 0.08, 0.25, "end")
    ]

    for text, cx, cy, btype in steps:
        if btype in ['start', 'end']:
            p = patches.FancyBboxPatch((cx - 0.065, cy - 0.12), 0.13, 0.24, boxstyle="round,pad=0.01,rounding_size=0.06",
                                       facecolor='#e2e8f0', edgecolor='#0f172a', lw=1.2)
        elif btype == 'decision':
            p = patches.RegularPolygon((cx, cy), numVertices=4, radius=0.12, orientation=0,
                                       facecolor='#fef3c7', edgecolor='#b45309', lw=1.2)
        else:
            p = patches.FancyBboxPatch((cx - 0.075, cy - 0.11), 0.15, 0.22, boxstyle="round,pad=0.01,rounding_size=0.02",
                                       facecolor='#ffffff', edgecolor='#0f172a', lw=1.2)
        ax.add_patch(p)
        ax.text(cx, cy, text, fontsize=7.2, fontweight='bold', ha='center', va='center', color='#0f172a')

    # Connectors
    # Row 1 left-to-right
    ax.annotate('', xy=(0.175, 0.75), xytext=(0.145, 0.75), arrowprops=dict(arrowstyle="->", lw=1.2, color='#0f172a'))
    ax.annotate('', xy=(0.365, 0.75), xytext=(0.325, 0.75), arrowprops=dict(arrowstyle="->", lw=1.2, color='#0f172a'))
    ax.annotate('', xy=(0.56, 0.75), xytext=(0.515, 0.75), arrowprops=dict(arrowstyle="->", lw=1.2, color='#0f172a'))
    ax.annotate('', xy=(0.765, 0.75), xytext=(0.72, 0.75), arrowprops=dict(arrowstyle="->", lw=1.2, color='#0f172a'))
    ax.text(0.74, 0.78, "Yes", fontsize=7, color='#15803d', fontweight='bold')

    # Decision No loop back
    ax.annotate('', xy=(0.44, 0.86), xytext=(0.64, 0.83),
                arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=-0.3", lw=1, color='#b91c1c', linestyle='--'))
    ax.text(0.54, 0.94, "No (Show error: exceed max marks)", fontsize=6.5, color='#b91c1c', ha='center')

    # Down from submit to admin
    ax.annotate('', xy=(0.84, 0.36), xytext=(0.84, 0.64), arrowprops=dict(arrowstyle="->", lw=1.2, color='#0f172a'))

    # Row 2 right-to-left
    ax.annotate('', xy=(0.72, 0.25), xytext=(0.765, 0.25), arrowprops=dict(arrowstyle="->", lw=1.2, color='#0f172a'))
    ax.annotate('', xy=(0.515, 0.25), xytext=(0.56, 0.25), arrowprops=dict(arrowstyle="->", lw=1.2, color='#0f172a'))
    ax.text(0.54, 0.28, "Yes", fontsize=7, color='#15803d', fontweight='bold')

    # Decision No return to faculty
    ax.annotate('', xy=(0.84, 0.64), xytext=(0.64, 0.37),
                arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=-0.2", lw=1, color='#b91c1c', linestyle='--'))
    ax.text(0.76, 0.49, "No (Reject to draft)", fontsize=6.5, color='#b91c1c')

    ax.annotate('', xy=(0.325, 0.25), xytext=(0.365, 0.25), arrowprops=dict(arrowstyle="->", lw=1.2, color='#0f172a'))
    ax.annotate('', xy=(0.145, 0.25), xytext=(0.175, 0.25), arrowprops=dict(arrowstyle="->", lw=1.2, color='#0f172a'))

    plt.tight_layout()
    plt.savefig('report_assets/fig_2_2_workflow.png', bbox_inches='tight', dpi=300)
    plt.close()
    print("Created fig_2_2_workflow.png")

if __name__ == '__main__':
    create_architecture_diagram()
    create_workflow_diagram()
