def plt_rss(data: list[float]):
    import matplotlib.pyplot as plt
    import numpy as np

    # Use integer indices for x-axis
    x = np.arange(len(data))
    y = np.array(data)
    fig, ax = plt.subplots(figsize=(10, 6))  # Create a figure of size 10x6 inches
    ax.plot(x, y, 'b-', linewidth=2, alpha=0.8, label='RSS usage')

    ax.set_xlabel('Time Sample Point (/1s)', fontsize=12)
    ax.set_ylabel('RSS Usage (/MB)', fontsize=12)
    ax.set_title('RSS Graph', fontsize=14)
    ax.grid(True, linestyle='--', alpha=0.7)

    # Set x-axis to show only integer points
    ax.set_xticks(np.arange(len(data)))

    # Ensure proper x-axis limits to show all integer points
    ax.set_xlim(-0.2, len(data) - 0.8)

    plt.tight_layout()
    plt.savefig('line_graph_demo.png', dpi=300, bbox_inches='tight')