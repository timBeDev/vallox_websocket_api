from .constants import vlxDevConstants
from .client import Client

import logging


def enum(*sequential, **named):
  enums = dict(zip(sequential, range(len(sequential))), **named)
  reverse = dict((value, key) for key, value in enums.items())
  enums['reverse_mapping'] = reverse
  return type('Enum', (), enums)

PROFILE = enum(
  NONE = 0,
  HOME = 1,
  AWAY = 2,
  BOOST = 3,
  FIREPLACE = 4,
  EXTRA = 5
)

MAP = {
  "temperature": {
      PROFILE.HOME: 'A_CYC_HOME_AIR_TEMP_TARGET',
      PROFILE.AWAY: 'A_CYC_AWAY_AIR_TEMP_TARGET',
      PROFILE.BOOST: 'A_CYC_BOOST_AIR_TEMP_TARGET'
  }
}

class Vallox(Client):
    def get_profile(self):
        """Returns the profile of the fan

        :returns: One of PROFILE.* values or PROFILE.NONE if unknown
        """
        s = self.fetch_metrics(['A_CYC_STATE','A_CYC_BOOST_TIMER',
                                'A_CYC_FIREPLACE_TIMER','A_CYC_EXTRA_TIMER'])

        if s['A_CYC_BOOST_TIMER'] > 0: return PROFILE.BOOST
        if s['A_CYC_FIREPLACE_TIMER'] > 0: return PROFILE.FIREPLACE
        if s['A_CYC_EXTRA_TIMER'] > 0: return PROFILE.EXTRA
        if s['A_CYC_STATE'] == 1: return PROFILE.AWAY
        elif s['A_CYC_STATE'] == 0: return PROFILE.HOME
        return PROFILE.NONE

    
    def set_profile(self, profile, duration=None):
        set_duration = None
        if duration is not None and 0 <= int(duration) <= 65535:
            set_duration = int(duration)

        """Set the profile of the unit

        :params:
          :profile: One of PROFILE.* values
          :duration: timeout in minutes for the FIREPLACE, BOOST and EXTRA profiles
        """

        #duration: None means default configured setting. 65535 means no time out

        if profile == PROFILE.HOME:
            logging.info('Setting unit to HOME profile')
            self.set_values({'A_CYC_STATE': '0',
                             'A_CYC_BOOST_TIMER': '0',
                             'A_CYC_FIREPLACE_TIMER': '0',
                             'A_CYC_EXTRA_TIMER': '0'})
        elif profile == PROFILE.AWAY:
            logging.info('Setting unit to AWAY profile')
            self.set_values({'A_CYC_STATE': '1',
                             'A_CYC_BOOST_TIMER': '0',
                             'A_CYC_FIREPLACE_TIMER': '0',
                             'A_CYC_EXTRA_TIMER': '0'})
        elif profile == PROFILE.FIREPLACE:
            if set_duration is not None:
                dur = str(set_duration)
            else:
                dur = str(self.fetch_metric('A_CYC_FIREPLACE_TIME'))
            logging.info('Setting unit to FIREPLACE profile for %s minutes', dur)
            self.set_values({'A_CYC_BOOST_TIMER': '0',
                             'A_CYC_FIREPLACE_TIMER': dur,
                             'A_CYC_EXTRA_TIMER': '0'})
        elif profile == PROFILE.BOOST:
            if set_duration is not None:
                dur = str(set_duration)
            else:
                dur = str(self.fetch_metric('A_CYC_BOOST_TIME'))
            logging.info('Setting unit to BOOST profile for %s minutes', dur)
            self.set_values({'A_CYC_BOOST_TIMER': dur,
                             'A_CYC_FIREPLACE_TIMER': '0',
                             'A_CYC_EXTRA_TIMER': '0'})
        elif profile == PROFILE.EXTRA:
            if set_duration is not None:
                dur = str(set_duration)
            else:
                dur = str(self.fetch_metric('A_CYC_EXTRA_TIME'))
                logging.info('Setting unit to EXTRA profile for %s minutes', dur)
            self.set_values({'A_CYC_BOOST_TIMER': '0',
                             'A_CYC_FIREPLACE_TIMER': '0',
                             'A_CYC_EXTRA_TIMER': dur})

    def get_temperature(self, profile):
        try:
            setting = MAP["temperature"][profile]
        except KeyError as e:
            raise AttributeError("Temperature is not gettable for this profile: " + str(profile))

        return self.fetch_metric(setting)

    def set_temperature(self, profile, temperature):
        try:
            setting = MAP["temperature"][profile]
        except KeyError as e:
            raise AttributeError("Temperature is not settable for this profile: " + str(profile))

        self.set_values({setting: temperature})
