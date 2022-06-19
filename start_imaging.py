"""
Test imaging
"""

import logging
import colorlog
from matplotlib import pyplot as plt
import numpy as np

# local imports
from hamamatsu import Hamamatsu


def setup_logging_handlers(level='INFO'):
    """
    This function sets up the error logging to the console. Logging
    can be set up at the top of each file by doing:
    import logging
    logger = logging.getLogger(__name__)
    """
    # get the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    # set up logging to console for INFO and worse
    sh = colorlog.StreamHandler()
    sh.setLevel(getattr(logging,level))

    sh_formatter = colorlog.ColoredFormatter("%(log_color)s%(levelname)-8s - "
                                             "%(name)-25s - %(threadName)-15s -"
                                             " %(asctime)s - %(cyan)s \n  "
                                             "%(message)s\n",
                                             datefmt=None,
                                             reset=True,
                                             log_colors={
                                                         'DEBUG':    'cyan',
                                                         'INFO':     'green',
                                                         'WARNING':  'yellow',
                                                         'ERROR':    'red',
                                                         'CRITICAL': 'red,'
                                                                     'bg_white',
                                                         },
                                             secondary_log_colors={},
                                             style='%'
                                             )
    sh.setFormatter(sh_formatter)

    # put the handlers to use
    root_logger.addHandler(sh)


if __name__ == '__main__':

    setup_logging_handlers()
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # camera settings
    shots = 10
    camera_settings = {
        'num_images': shots,
        'analog_gain': 1,
        'exposure_time': 1e-3,
        'em_gain': 10,
        # 'trigger_polarity': ,
        # 'external_trigger_mode': ,
        # 'scan_speed': ,
        # 'external_trigger_source': ,
        'scan_mode': "SMD N",
        'super_pixel_binning': "SPX 1",
        'num_img_buffers': shots,
        'shots_per_measurement': 1,
        'low_light_sensitivity': "LLS 0",
        'cooling': "CSW O",
        'fan': "FAN O",
    }

    # instantiate Hamamatsu
    H = Hamamatsu(**camera_settings)
    H.init()
    logger.info("Initialized Hamamatsu")

    # check select camera settings
    H.check_camera_setting("TMP") # temp, C
    H.check_camera_setting("AET") # exposure time, s

    # setup up plotting. take 1 shot.
    fig,axes = plt.subplots(nrows=2,ncols=1,sharex='all')
    fig.clf()
    ax1,ax2 = axes
    H.get_data()
    data = H.last_measurement[0, :, :]
    cax = ax1.imshow(data, cmap='gray')
    fig.colorbar(cax, ax=ax1)
    line, = ax2.plot(data[data.shape[0]//2,:])
    plt.show()

    def on_close(event):
        """close the session"""
        H.close()

    fig.canvas.mpl_connect('close_event', on_close)

    # do a measurement, i.e. get data
    for s in range(shots-1):
        H.get_data()
        data = H.last_measurement[0,:,:]
        logger.info(data.shape)

        cax.set_data(data)
        line.set_data(range(512), data[data.shape[0]//2,:])
        cax.axes.set_title(H.session.hamamatsu_serial("?TMP", "?TMP"))
        fig.canvas.draw()
        fig.canvas.flush_events()