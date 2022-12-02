from taxes.class_tax_canada import TaxCanada

class TaxFallback(TaxCanada):
    """Fallback tax"""

    def _set_variables(self):
        # super()._set_variables()
        self._provincial_tax = self._tax['attributes']["fallback_tax"]
        self._tax_name = self._tax['attributes']["tax_type"]

    def _calculate_excise_tax(self):
        return 0
