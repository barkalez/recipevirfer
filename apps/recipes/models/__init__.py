from django.db import models

from apps.recipes.services.text_normalization import normalize_spanish_term

class NutritionalInfoIngredient(models.Model):
    SOURCE_CSV = "csv_import"
    SOURCE_USDA = "usda_api"
    SOURCE_CHOICES = (
        (SOURCE_CSV, "CSV import"),
        (SOURCE_USDA, "USDA API"),
    )

    source_id = models.PositiveIntegerField(unique=True, db_index=True)
    fdc_id = models.BigIntegerField(null=True, blank=True, unique=True, db_index=True)
    name = models.CharField(max_length=300, db_index=True)
    normalized_name = models.CharField(max_length=300, db_index=True, default="")
    scientific_name = models.CharField(max_length=300, blank=True, default="")
    source_name_en = models.CharField(max_length=300, blank=True, default="")
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default=SOURCE_CSV, db_index=True)
    edible_portion = models.FloatField(null=True, blank=True)
    energy_total = models.FloatField(null=True, blank=True)
    protein_total = models.FloatField(null=True, blank=True)
    nutrients = models.JSONField(default=dict, blank=True)
    source_payload = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        self.normalized_name = normalize_spanish_term(self.name)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.source_id} - {self.name}"


class IngredientSearchAlias(models.Model):
    alias_es = models.CharField(max_length=150, unique=True)
    alias_normalized = models.CharField(max_length=150, unique=True, db_index=True)
    usda_query_en = models.CharField(max_length=150)
    ingredient = models.ForeignKey(
        NutritionalInfoIngredient,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="search_aliases",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["alias_es"]

    def save(self, *args, **kwargs):
        self.alias_normalized = normalize_spanish_term(self.alias_es)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.alias_es} -> {self.usda_query_en}"


class CulinaryUnit(models.Model):
    SOURCE_SEED = "seed"
    SOURCE_MANUAL = "manual"
    SOURCE_CHOICES = (
        (SOURCE_SEED, "Seed"),
        (SOURCE_MANUAL, "Manual"),
    )

    name = models.CharField(max_length=120, unique=True)
    normalized_name = models.CharField(max_length=120, unique=True, db_index=True)
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default=SOURCE_SEED, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        self.normalized_name = normalize_spanish_term(self.name)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


class CulinaryAction(models.Model):
    SOURCE_SEED = "seed"
    SOURCE_MANUAL = "manual"
    SOURCE_CHOICES = (
        (SOURCE_SEED, "Seed"),
        (SOURCE_MANUAL, "Manual"),
    )

    name = models.CharField(max_length=150, unique=True)
    normalized_name = models.CharField(max_length=150, unique=True, db_index=True)
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default=SOURCE_SEED, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        self.normalized_name = normalize_spanish_term(self.name)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


class CulinaryParticiple(models.Model):
    SOURCE_SEED = "seed"
    SOURCE_MANUAL = "manual"
    SOURCE_CHOICES = (
        (SOURCE_SEED, "Seed"),
        (SOURCE_MANUAL, "Manual"),
    )

    name = models.CharField(max_length=120, unique=True)
    normalized_name = models.CharField(max_length=120, unique=True, db_index=True)
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default=SOURCE_SEED, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        self.normalized_name = normalize_spanish_term(self.name)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name
