import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


def ShowPlots():
    """Method to show all plots stored in memory. We use a custom method for
    completeness sake, in case we decide in the future to use something
    other than MATPLOTLIB"""

    plt.show()


def GenericPlot(xData: list, yData: list, xlabel: str, ylabel: str, title: str, mylegend: list):
    """
    Function to generate a generic plot using MatplotLib.
    """

    fig_total, ax_total = plt.subplots()

    # define plot elements
    """
        plt.hlines(y=Stats.TwoPercent, xmin=1, xmax=x_length,
                   color='black', linestyles='dotted')
        """

    # main title
    plt.suptitle(f'{title}', weight="bold", size='x-large')
    plt.grid(which='both')

    # define plot parameters
    ax_total.plot(xData, yData, '--*', label=mylegend)
    """
        ax_total.yaxis.set_major_formatter(
            plt.FuncFormatter(self.FormatterTime))
        """
    ax_total.set_xlabel(xlabel)
    ax_total.set_ylabel(ylabel)
    legend = ax_total.legend()

    # plt.show()


def DynamicPlot(x_data, y_data):
    """
    WORK IN PROGRESS USE DYNAMICPLOT2 AS AN ALTERNATIVE
    Function to plot data dynamically.
    x_data and y_data should be passed as empty lists ideally ?
    We will see...
    """
    figure = plt.figure()
    line, = plt.plot(x_data, y_data, '-')

    def update(frame):
        x_data.append(1)
        y_data.append(1)
        line.set_data(x_data, y_data)
        figure.gca().relim()
        figure.gca().autoscale_view()
        return line,

    animation = FuncAnimation(figure, update, interval=200)

    # pyplot.show()


def DynamicPlot2(x_data, y_data, x_label: str, y_label: str, title: str):

    plt.suptitle(f'{title}', weight="bold", size='x-large')
    plt.grid(which='both')
    plt.xlabel(x_label)
    plt.ylabel(y_label)

    plt.plot(x_data, y_data, '--*')
    plt.pause(0.1)
