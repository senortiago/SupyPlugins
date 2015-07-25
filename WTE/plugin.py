###
# Copyright (c) 2014-2015, James Lu
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

###

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks

import random
import json
try: # Python 3
    from urllib.parse import urlencode
except ImportError: # Python 2
    raise callbacks.Error('This plugin requires Python 3!')

try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('WTE')
except ImportError:
    # Placeholder that allows to run the plugin on a bot
    # without the i18n module
    _ = lambda x:x

class WTE(callbacks.Plugin):
    """Worst Translations Ever! plugin. Translates text through
    multiple rounds of Google Translate to get amazing results!"""
    threaded = True

    def __init__(self, irc):
        self.__parent = super(WTE, self)
        self.__parent.__init__(irc)
        self.langs = ('sw', 'sv', 'is', 'et', 'te', 'tr', 'mr', 'nl', 'sl', 
        'id', 'gu', 'hi', 'az', 'hmn', 'ko', 'da', 'bg', 'lo', 'so', 'tl', 
        'hu', 'ca', 'cy', 'bs', 'ka', 'vi', 'eu', 'ms', 'fr', 'no', 'hy', 
        'ro', 'ru', 'th', 'it', 'ta', 'sq', 'ceb', 'bn', 'de', 'zh-CN', 
        'be', 'lt', 'ne', 'fi', 'pa', 'iw', 'km', 'mt', 'ht', 'mi', 'lv', 
        'jw', 'sr', 'ar', 'ig', 'ha', 'pt', 'ga', 'af', 'zu', 'la', 'el', 
        'cs', 'uk', 'ja', 'hr', 'kn', 'gl', 'mk', 'fa', 'sk', 'mn', 'es', 
        'ur', 'pl', 'eo', 'yo', 'en', 'yi')

    def _jsonRepair(self, data):
        while ',,' in data:
            data = data.replace(',,', ',null,')
        while '[,' in data:
            data = data.replace('[,', '[')
        return data

    def getTranslation(self, irc, sourceLang, targetLang, text):
        args = {"sl": sourceLang, "tl": targetLang, 'q': text}
        url = "https://translate.googleapis.com/translate_a/single?client=gtx&dt=t&"+ \
            urlencode(args)
        self.log.debug("WTE: Using URL %s", url)
        headers = {'User-Agent': ('Mozilla/5.0 (X11; Linux i586; rv:31.0) '
                                 'Gecko/20100101 Firefox/31.0')}
        try:
            data = utils.web.getUrlFd(url, headers).read().decode("utf-8")
        except utils.web.Error as e:
            irc.error(str(e), Raise=True)
        data = self._jsonRepair(data)
        data = json.loads(data)
        return ''.join(x[0] for x in data[0])

    def wte(self, irc, msg, args, text):
        """wte <text>

        Worst Translations Ever! plugin. Translates <text> through
        multiple rounds of Google Translate to get amazing results!
        """
        outlang = self.registryValue('language', msg.args[0])
        if outlang not in self.langs:
            irc.error("Unrecognized output language. Please set "
                "'config plugins.wte.language' correctly.", Raise=True)
        ll = random.sample(self.langs, random.randint(4,8))
        self.log.debug(format("WTE: Using %i languages: %L "
            "(outlang %s)", len(ll), ll, outlang))
        for targetlang in ll:
            text = self.getTranslation(irc, "auto", targetlang, text)
        text = self.getTranslation(irc, "auto", outlang, text)
        text = text.strip()
        if self.registryValue("verbose", msg.args[0]):
            irc.reply(format("Translated through \x02%i\x02 languages: %L "
                "(outlang %s)",
                len(ll), ll, outlang))
        irc.reply(text)
    wte = wrap(wte, ['text'])

Class = WTE

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79: