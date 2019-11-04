from django.db import models

class Study(models.Model):
    author = models.CharField(max_length=50, verbose_name="First Author (Surname Initials)")
    consortium = models.CharField(max_length=50, verbose_name="Consortium", blank=True)
    pmid = models.CharField(max_length=20, verbose_name="PubMed ID (or DOI)")
    publication_date = models.DateField(verbose_name="Publication Date (DD/MM/YY)")
    trait = models.CharField(max_length=100, verbose_name="Trait")
    efo = models.CharField(max_length=50, verbose_name="EFO Term", blank=True)
    analysis = models.CharField(max_length=100, verbose_name="Analysis (e.g. Discovery or Discovery and replication)", blank=True)
    source = models.CharField(max_length=50, verbose_name="Source (e.g. Table 1, Table S1)", blank=True)
    date_added = models.DateField(auto_now=True, verbose_name="Date Added")
    user = models.CharField(max_length=50, verbose_name="User ID")
    id = models.CharField(max_length=200, primary_key=True, verbose_name="ID")

    class Meta:
        db_table = 'study'
        verbose_name_plural = "studies"

    def __str__(self):
        return self.id

class Analysis(models.Model):
    outcome = models.CharField(max_length=200, verbose_name="Outcome (eg. DNA methylation)")
    exposure = models.CharField(max_length=200, verbose_name="Exposure (eg. the Trait)")
    covariates = models.CharField(max_length=300, blank=True, verbose_name="Covariates (eg. Age, sex and smoking)")
    outcome_unit = models.CharField(max_length=50, blank=True, verbose_name="Outcome Units")
    exposure_unit = models.CharField(max_length=50, blank=True, verbose_name="Exposure Units")
    array = models.CharField(max_length=50, verbose_name="Methylation Array")
    tissue = models.CharField(max_length=100, verbose_name="Tissue")
    further_details = models.CharField(max_length=200, blank=True, verbose_name="Further Details")
    id = models.CharField(primary_key=True, max_length=200, verbose_name="ID")

    class Meta:
        db_table = 'analysis'
        verbose_name_plural = "analyses"

    def __str__(self):
        return self.id

class Participants(models.Model):
    n = models.CharField(max_length=20, verbose_name="Total Number of Participants")
    n_studies = models.CharField(max_length=20, verbose_name="Total Number of Cohorts")
    categories = models.CharField(max_length=200, blank=True, verbose_name="Categories (eg. 200 smokers, 200 non-smokers)")
    age = models.CharField(max_length=5, blank=True, verbose_name="Age (in years)")
    n_males = models.CharField(max_length=20, blank=True, verbose_name="Total Number of Males")
    n_females = models.CharField(max_length=20, blank=True, verbose_name="Total Number of Females")
    n_eur = models.CharField(max_length=20, blank=True, verbose_name="Total Number of Europeans")
    n_eas = models.CharField(max_length=20, blank=True, verbose_name="Total Number of East Asians")
    n_sas = models.CharField(max_length=20, blank=True, verbose_name="Total Number of South Asians")
    n_afr = models.CharField(max_length=20, blank=True, verbose_name="Total Number of Africans")
    n_amr = models.CharField(max_length=20, blank=True, verbose_name="Total Number of Admixed Americans (eg. Mexican)")
    n_oth = models.CharField(max_length=20, blank=True, verbose_name="Total Number of Other Ancestry")
    id = models.CharField(primary_key=True, max_length=200, verbose_name="ID")

    class Meta:
        db_table = 'participants'
        verbose_name_plural = "participants"

    def __str__(self):
        return self.id

class Results(models.Model):
    cpg = models.CharField(max_length=20, verbose_name="CpG")
    beta = models.CharField(max_length=20, blank=True, verbose_name="Beta")
    se = models.CharField(max_length=20, blank=True, verbose_name="SE")
    p = models.CharField(max_length=20, verbose_name="P-value")
    i2 = models.CharField(max_length=20, blank=True, verbose_name="I2")
    p_het = models.CharField(max_length=20, blank=True, verbose_name="P-value Heterogeneity")
    details = models.CharField(max_length=200, blank=True, verbose_name="Details")
    #dmr = models.CharField(max_length=20, choices=(('No', 'No'), ('Yes', 'Yes'),), default="No", verbose_name="Differentially Methylated Region Analysis")
    study_id = models.CharField(max_length=200, blank=True, default="pmid_trait_analysis")

    class Meta:
        db_table = 'results'
        verbose_name_plural = "results"

    def __str__(self):
        return self.study_id

