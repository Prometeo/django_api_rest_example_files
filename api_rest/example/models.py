from django.db import models
from django.contrib.postgres.fields import JSONField
from django.core.validators import MaxValueValidator
from safedelete.models import SafeDeleteModel, SOFT_DELETE, SOFT_DELETE_CASCADE
from users.models import BlappUser
from profiles.models import Plan


class InvoiceCounter(SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE

    BOLETA = 'BOLETA'
    FACTURA = 'FACTURA'
    INVOICE_TYPE = [
        (BOLETA, 'BOLETA'),
        (FACTURA, 'FACTURA')
    ]
    invoice_type = models.CharField(
        verbose_name=u'Tipo de recibo',
        choices=INVOICE_TYPE,
        max_length=20,
        blank=True,
        null=True
    )
    prefix_counter = models.PositiveSmallIntegerField(
        validators=[MaxValueValidator(999)], default=1)
    sufix_counter = models.PositiveSmallIntegerField(
        validators=[MaxValueValidator(999)], default=1)

    def get_next_correlative(self):
        next_correlative = self.sufix_counter + 1
        if next_correlative > 999:
            return (self.prefix_counter + 1, 1)
        return (self.prefix_counter, next_correlative)

    class Meta():
        db_table = "invoice_counter"
        verbose_name = "Correlativo de Boletas y Facturas"
        verbose_name_plural = "Correlativo de Boletas y Facturas"

    def __str__(self):
        return self.invoice_type

    def get_next_correlative(self):
        next_correlative = self.sufix_counter + 1
        if next_correlative > 999:
            return (self.prefix_counter + 1, 1)
        return (self.prefix_counter, next_correlative)
    # invoice_counter = InvoiceCounter.objects.get(
    #             invoice_type=self.user_profile.receipt_type)
    #         self.invoice_counter_prefix, self.invoice_counter_sufix = invoice_counter.get_next_correlative()



class InvoiceUser(SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE
    invoice_zip = models.FileField(
        upload_to="invoices/pdf",
        blank=True,
        null=True,
        verbose_name="Recibos de Usuarios"
    )
    user = models.ForeignKey(
        BlappUser,
        on_delete=models.CASCADE,
    )

    class Meta:
        db_table = "invoice_user"


