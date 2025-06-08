import matplotlib.pyplot as plt
import seaborn as sns

def plot_chart(df, x, y, group_by, chart_type, custom_title="", x_title="", y_title="", style_col=None, condition=None):
    title = custom_title if custom_title else f"{y} por {x}"
    xlabel = x_title if x_title else x
    ylabel = y_title if y_title else y

    # Crear columna para leyenda combinada
    if group_by:
        grouped_df = df.copy()
        grouped_df["__hue__"] = grouped_df[group_by].astype(str).agg("+".join, axis=1)
    else:
        grouped_df = df.copy()

    fig, ax = plt.subplots(figsize=(18, 12))
    hue_col = "__hue__" if group_by else None

    if style_col and condition:
        # Evaluamos la condición solo una vez y la añadimos como columna auxiliar
        try:
            grouped_df["__highlight__"] = grouped_df.eval(f"`{style_col}` {condition}")
        except Exception as e:
            grouped_df["__highlight__"] = False
            print(f"❌ Condición no válida para {style_col}: {condition} ({e})")
    else:
        grouped_df["__highlight__"] = False

    if chart_type == "Barras":
        grouped_plot_df = grouped_df.groupby([x, "__hue__"] if group_by else [x])[y].mean().reset_index()
        grouped_plot_df["__highlight__"] = grouped_df.groupby([x, "__hue__"] if group_by else [x])["__highlight__"].any().values
        for _, row in grouped_plot_df.iterrows():
            hatch = "//" if row["__highlight__"] else None
            color = sns.color_palette()[0]
            ax.bar(row[x], row[y], label=row["__hue__"] if group_by else row[x], hatch=hatch, edgecolor="black", color=color)

    elif chart_type == "Línea":
        grouped_plot_df = grouped_df.groupby([x, "__hue__"] if group_by else [x])[y].mean().reset_index()
        grouped_plot_df["__highlight__"] = grouped_df.groupby([x, "__hue__"] if group_by else [x])["__highlight__"].any().values
        for name, group in grouped_plot_df.groupby("__hue__" if group_by else x):
            linestyle = "--" if group["__highlight__"].any() else "-"
            ax.plot(group[x], group[y], label=name, linestyle=linestyle, marker='o')

    elif chart_type == "Boxplot":
        sns.boxplot(
            data=grouped_df,
            x=x,
            y=y,
            hue=hue_col,
            ax=ax
        )

    elif chart_type == "Puntos":
        sns.scatterplot(
            data=grouped_df,
            x=x,
            y=y,
            hue=hue_col,
            ax=ax,
            s=100,
            alpha=0.7
        )

    ax.set_title(title, fontsize=16)
    ax.set_xlabel(xlabel, fontsize=14)
    ax.set_ylabel(ylabel, fontsize=14)
    ax.tick_params(axis='x', rotation=30)
    ax.legend(loc='best', title=" + ".join(group_by) if group_by else "")
    return fig
