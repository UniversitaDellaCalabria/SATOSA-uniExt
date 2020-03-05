import re
from satosa.micro_services.processors.base_processor import BaseProcessor


class UniAttributeProcessor:
    @staticmethod
    def codice_fiscale_rs(schacpersonaluniqueids=[], nationprefix=False, nationprefix_sep=':'):
        if isinstance(schacpersonaluniqueids, str):
            schacpersonaluniqueids = [schacpersonaluniqueids]
        # R&S format
        rs_regexp = (r'(?P<urn_prefix>urn:schac:personalUniqueID:)?'
                     r'(?P<nation>[a-zA-Z]{2}):'
                     r'(?P<doc_type>[a-zA-Z]{2,3}):(?P<uniqueid>[\w]+)')
        for uniqueid in schacpersonaluniqueids:
            result = re.match(rs_regexp, uniqueid, re.I)
            if result:
                data = result.groupdict()
                #if data.get('nation') == 'IT' and data.get('doc_type') in  ['CF', 'TIN']:
                if nationprefix:
                    # returns IT:CODICEFISCALE
                    return nationprefix_sep.join((data['nation'],
                                                  data['uniqueid']))
                # returns CODICEFISCALE
                return data['uniqueid']

    @staticmethod
    def codice_fiscale_spid(fiscalNumbers, nationprefix=False, nationprefix_sep=':'):
        if isinstance(fiscalNumbers, str):
            fiscalNumbers = [fiscalNumbers]
        # SPID/eIDAS FORMAT
        spid_regexp = r'(?P<prefix>TIN)(?P<nation>[a-zA-Z]{2})-(?P<uniqueid>[\w]+)'
        for fiscalNumber in fiscalNumbers:
            result = re.match(spid_regexp, fiscalNumber, re.I)
            if result:
                data = result.groupdict()
                if nationprefix:
                    # returns IT:CODICEFISCALE
                    return nationprefix_sep.join((data['nation'],
                                                  data['uniqueid']))
                # returns CODICEFISCALE
                return data['uniqueid']

    @staticmethod
    def matricola(personalUniqueCodes=[], id_string='dipendente', orgname='unical.it'):
        if isinstance(personalUniqueCodes, str):
            personalUniqueCodes = [personalUniqueCodes]
        _regexp = (r'(?P<urn_prefix>urn:schac:personalUniqueCode:)?'
                   r'(?P<nation>[a-zA-Z]{2}):'
                   #r'(?P<organization>[a-zA-Z\.\-]+):'
                   'ORGNAME:'
                   'IDSTRING:'
                   r'(?P<uniqueid>[\w]+)').replace('IDSTRING', id_string).replace('ORGNAME', orgname)
        for uniqueid in personalUniqueCodes:
            result = re.match(_regexp, uniqueid, re.I)
            if result:
                return result.groupdict()['uniqueid']


class UnicalLegacyAttributeGenerator(BaseProcessor):

    def matricola_dipendente(self, attributes):
        v = None
        if attributes.get('schacpersonaluniquecode'):
            v = 'schacpersonaluniquecode'
        elif attributes.get('schacPersonalUniqueCode'):
            v = 'schacPersonalUniqueCode'
        if v:
            return UniAttributeProcessor.matricola(attributes[v],
                                                   id_string='dipendente')

    def matricola_studente(self, attributes):
        v = None
        if attributes.get('schacpersonaluniquecode'):
            v = 'schacpersonaluniquecode'
        elif attributes.get('schacPersonalUniqueCode'):
            v = 'schacPersonalUniqueCode'
        if v:
            return UniAttributeProcessor.matricola(attributes[v],
                                                   id_string='studente')

    def codice_fiscale(self, attributes):
        v = None
        if attributes.get('schacpersonaluniqueid'):
            return UniAttributeProcessor.codice_fiscale_rs(attributes['schacpersonaluniqueid'])
        elif attributes.get('schacPersonalUniqueID'):
            return UniAttributeProcessor.codice_fiscale_rs(attributes['schacPersonalUniqueID'])
        elif attributes.get('fiscalNumber'):
            v = 'fiscalNumber'
        elif attributes.get('fiscalnumber'):
            v = 'fiscalnumber'
        if v:
            fiscalNumber = UniAttributeProcessor.codice_fiscale_spid(attributes[v])
            # put a fake 'schacpersonaluniqueid' to do ldap account linking with the next microservice
            attributes['schacpersonaluniqueid'] = 'urn:schac:personalUniqueID:IT:CF:{}'.format(fiscalNumber)
            return fiscalNumber

    def process(self, internal_data, attribute, **kwargs):
        if hasattr(self, attribute) and callable(getattr(self, attribute)):
            internal_data.attributes[attribute] = getattr(self, attribute)(internal_data.attributes)
