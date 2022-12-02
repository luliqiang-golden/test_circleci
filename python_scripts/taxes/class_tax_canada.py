from taxes.class_tax_base import TaxBase, TaxType


class TaxCanada(TaxBase): 
    
    _federal_flat_rate = 0
    _federal_ad_valorem = 0
    _provincial_flat_rate = 0
    _provincial_ad_valorem = 0
    _adjustment = 0    

    _cannabis_duty_flat_rate = 0
    _cannabis_duty_ad_valorem = 0
    _canabis_duty_greater = 0
    _additional_cannabis_duty_flat_rate = 0
    _additional_cannabis_duty_ad_valorem = 0
    _additional_canabis_duty_greater = 0
    _additional_canabis_duty_type = ""
    _adjustment_to_additional_cannabis_duty = 0
    _subtotal = 0
    _provincial_tax = 0
    _total = 0

    def _set_variables(self):
        self._provincial_tax = self._tax['attributes'][self._tax_provincial]    
        if (self._tax['province'] == 'ON'):
            if(self._type == TaxType.FLOWERING):
                self._federal_flat_rate = float(self._tax['attributes']["flowering_federal_flat_rate"])
                self._federal_ad_valorem = float(self._tax['attributes']["flowering_federal_ad_valorem"])
                self._provincial_flat_rate = float(self._tax['attributes']["flowering_provincial_flat_rate"])
                self._provincial_ad_valorem = float(self._tax['attributes']["flowering_provincial_ad_valorem"])
                self._adjustment = float(self._tax['attributes']["flowering_adjustment"])
            elif (self._type == TaxType.NON_FLOWERING):
                self._federal_flat_rate = float(self._tax['attributes']["non_flowering_federal_flat_rate"])
                self._federal_ad_valorem = float(self._tax['attributes']["non_flowering_federal_ad_valorem"])
                self._provincial_flat_rate = float(self._tax['attributes']["non_flowering_provincial_flat_rate"])
                self._provincial_ad_valorem = float(self._tax['attributes']["non_flowering_provincial_ad_valorem"])
                self._adjustment = float(self._tax['attributes']["non_flowering_adjustment"])
            elif (self._type == TaxType.EXTRACT_OIL):
                self._federal_flat_rate = float(self._tax['attributes']["extract_federal_flat_rate"])
                self._federal_ad_valorem = float(self._tax['attributes']["extract_federal_ad_valorem"])
                self._provincial_flat_rate = float(self._tax['attributes']["extract_provincial_flat_rate"])
                self._provincial_ad_valorem = float(self._tax['attributes']["extract_provincial_ad_valorem"])
                self._adjustment =float(self._tax['attributes']["extract_adjustment"])
    
    def _execute_formulas(self):
        excise_value = self._calculate_excise_tax()
        provincial_value = self._calculate_provincial_tax()

        return {
            "excise_tax": excise_value,
            "provincial_tax": provincial_value            
        }
        
    
    def _calculate_excise_tax(self):
        # ad valorem are only calculated for flowering and non-flowering
        if (self._type != TaxType.EXTRACT_OIL):
            self._cannabis_duty_ad_valorem = self._get_total() * (1/(1 + self._federal_ad_valorem + ( self._provincial_ad_valorem + self._adjustment)) * self._federal_ad_valorem)
            self._canabis_duty_greater = self._cannabis_duty_flat_rate if self._cannabis_duty_flat_rate > self._cannabis_duty_ad_valorem else self._cannabis_duty_ad_valorem
            amount_sold = float(self._serialized_stats["qty"])
        else:
            amount_sold = 600


        self._cannabis_duty_flat_rate =  amount_sold * self._federal_flat_rate    

        self._additional_cannabis_duty_flat_rate = amount_sold * self._provincial_flat_rate
        # ad valorem are only calculated for flowering and non-flowering
        if (self._type != TaxType.EXTRACT_OIL):
            self._additional_cannabis_duty_ad_valorem = self._get_total() * (1/(1 + self._federal_ad_valorem + ( self._provincial_ad_valorem + self._adjustment)) * self._provincial_ad_valorem)
            self._additional_canabis_duty_type = "FLAT-RATE" if self._additional_cannabis_duty_flat_rate > self._additional_cannabis_duty_ad_valorem else "AD VALOREM"

        self._additional_canabis_duty_greater = self._additional_cannabis_duty_flat_rate if self._additional_cannabis_duty_flat_rate > self._additional_cannabis_duty_ad_valorem else self._additional_cannabis_duty_ad_valorem
            
        if (self._additional_canabis_duty_type == "FLAT-RATE" or self._type == TaxType.EXTRACT_OIL):
             self._adjustment_to_additional_cannabis_duty = (((self._get_total()-self._cannabis_duty_flat_rate)-self._additional_canabis_duty_greater)*(1/(1+self._adjustment))*self._adjustment)
        else:
            self._adjustment_to_additional_cannabis_duty = (self._get_total()*(1/(1+ self._federal_ad_valorem+(self._provincial_ad_valorem + self._adjustment)))*self._adjustment)

        self._cannabis_duty_flat_rate = round(self._cannabis_duty_flat_rate,2)
        self._cannabis_duty_ad_valorem = round(self._cannabis_duty_ad_valorem,2)
        self._canabis_duty_greater = round(self._canabis_duty_greater,2)
        self._additional_cannabis_duty_flat_rate = round(self._additional_cannabis_duty_flat_rate,2)
        self._additional_cannabis_duty_ad_valorem = round(self._additional_cannabis_duty_ad_valorem,2)
        self._additional_canabis_duty_greater = round(self._additional_canabis_duty_greater,2)
        self._adjustment_to_additional_cannabis_duty = round(self._adjustment_to_additional_cannabis_duty,2)
 
        return self._adjustment_to_additional_cannabis_duty


    def _calculate_provincial_tax(self):
        tax_name = self._tax_name
        if tax_name == 'fallback_tax_value':
            return (float(self._price) * float(self._provincial_tax)) / 100
        else:
            return float(self._price) * float(self._provincial_tax)
            