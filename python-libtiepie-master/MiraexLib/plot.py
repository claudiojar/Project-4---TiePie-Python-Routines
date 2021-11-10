import matplotlib.pyplot as plt

def ShowPlots():
        """Method to show all plots stored in memory. We use a custom method for
        completeness sake, in case we decide in the future to use something
        other than MATPLOTLIB"""

        plt.show()

def GenericPlot(self, xData: list, yData: list,
                    xlabel: str, ylabel: str, title: str,
                    mylegend : list):
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