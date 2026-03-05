from django.db import models


class CsvIngredient(models.Model):
    fdc_id = models.BigIntegerField(unique=True, db_index=True)
    alimento = models.CharField(max_length=300, db_index=True)
    nutrientes = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["alimento"]

    def __str__(self) -> str:
        return f"{self.fdc_id} - {self.alimento}"
