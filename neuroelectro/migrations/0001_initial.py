# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.auth.models
import django.utils.timezone
from django.conf import settings
import django.core.validators
import picklefield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(null=True, verbose_name='last login', blank=True)),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, max_length=30, validators=[django.core.validators.RegexValidator('^[\\w.@+-]+$', 'Enter a valid username. This value may contain only letters, numbers and @/./+/-/_ characters.', 'invalid')], help_text='Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.', unique=True, verbose_name='username')),
                ('first_name', models.CharField(max_length=30, verbose_name='first name', blank=True)),
                ('last_name', models.CharField(max_length=30, verbose_name='last name', blank=True)),
                ('email', models.EmailField(max_length=254, verbose_name='email address', blank=True)),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('lab_head', models.CharField(max_length=50, null=True, blank=True)),
                ('lab_website_url', models.CharField(max_length=200, null=True, blank=True)),
                ('last_update', models.DateTimeField(auto_now=True, null=True)),
                ('is_curator', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
            },
            managers=[
                (b'objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='API',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('path', models.CharField(max_length=200)),
                ('ip', models.GenericIPAddressField()),
                ('time', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=500)),
                ('abstract', models.CharField(max_length=10000, null=True)),
                ('pmid', models.IntegerField()),
                ('full_text_link', models.CharField(max_length=1000, null=True)),
                ('pub_year', models.IntegerField(null=True)),
                ('author_list_str', models.CharField(max_length=500, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ArticleFullText',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('full_text_file', models.FileField(null=True, upload_to=b'full_texts')),
                ('article', models.ForeignKey(to='neuroelectro.Article')),
            ],
        ),
        migrations.CreateModel(
            name='ArticleFullTextStat',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('metadata_processed', models.BooleanField(default=False)),
                ('metadata_human_assigned', models.BooleanField(default=False)),
                ('neuron_article_map_processed', models.BooleanField(default=False)),
                ('data_table_ephys_processed', models.BooleanField(default=False)),
                ('num_unique_ephys_concept_maps', models.IntegerField(null=True)),
                ('methods_tag_found', models.BooleanField(default=False)),
                ('date_mod', models.DateTimeField(auto_now=True)),
                ('article_full_text', models.ForeignKey(to='neuroelectro.ArticleFullText')),
            ],
        ),
        migrations.CreateModel(
            name='ArticleMetaDataMap',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_mod', models.DateTimeField(auto_now=True)),
                ('times_validated', models.IntegerField(default=0, null=True)),
                ('note', models.CharField(max_length=200, null=True)),
                ('added_by', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True)),
                ('article', models.ForeignKey(to='neuroelectro.Article')),
            ],
        ),
        migrations.CreateModel(
            name='ArticleSummary',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('num_nedms', models.IntegerField(null=True)),
                ('date_mod', models.DateTimeField(auto_now=True)),
                ('data', models.TextField(default=b'')),
                ('num_neurons', models.IntegerField(null=True)),
                ('article', models.ForeignKey(to='neuroelectro.Article')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Author',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('first', models.CharField(max_length=100, null=True)),
                ('middle', models.CharField(max_length=100, null=True)),
                ('last', models.CharField(max_length=100, null=True)),
                ('initials', models.CharField(max_length=10, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='BrainRegion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=500)),
                ('abbrev', models.CharField(max_length=10)),
                ('isallen', models.BooleanField(default=False)),
                ('allenid', models.IntegerField(default=0, null=True)),
                ('treedepth', models.IntegerField(null=True)),
                ('color', models.CharField(max_length=10, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ContValue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('mean', models.FloatField()),
                ('stdev', models.FloatField(null=True)),
                ('stderr', models.FloatField(null=True)),
                ('min_range', models.FloatField(null=True)),
                ('max_range', models.FloatField(null=True)),
                ('n', models.IntegerField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='DataSource',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='DataTable',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_mod', models.DateTimeField(auto_now=True)),
                ('link', models.CharField(max_length=1000, null=True)),
                ('table_html', picklefield.fields.PickledObjectField(null=True, editable=False)),
                ('table_text', models.CharField(max_length=10000, null=True)),
                ('needs_expert', models.BooleanField(default=False)),
                ('note', models.CharField(max_length=500, null=True)),
                ('article', models.ForeignKey(to='neuroelectro.Article')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='EphysConceptMap',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ref_text', models.CharField(max_length=200, null=True)),
                ('match_quality', models.IntegerField(null=True)),
                ('dt_id', models.CharField(max_length=20, null=True)),
                ('date_mod', models.DateTimeField(auto_now=True)),
                ('times_validated', models.IntegerField(default=0)),
                ('note', models.CharField(max_length=200, null=True)),
                ('added_by', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='EphysProp',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('nlex_id', models.CharField(max_length=100, null=True)),
                ('definition', models.CharField(max_length=1000, null=True)),
                ('norm_criteria', models.CharField(max_length=1000, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='EphysProperty',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ephys_name', models.CharField(max_length=255)),
                ('ephys_value', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='EphysPropSummary',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('num_nedms', models.IntegerField(null=True)),
                ('date_mod', models.DateTimeField(auto_now=True)),
                ('data', models.TextField(default=b'')),
                ('num_articles', models.IntegerField(null=True)),
                ('num_neurons', models.IntegerField(null=True)),
                ('value_mean_neurons', models.FloatField(null=True)),
                ('value_mean_articles', models.FloatField(null=True)),
                ('value_sd_neurons', models.FloatField(null=True)),
                ('value_sd_articles', models.FloatField(null=True)),
                ('ephys_prop', models.ForeignKey(to='neuroelectro.EphysProp')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='EphysPropSyn',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('term', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='ExpFactConceptMap',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ref_text', models.CharField(max_length=200, null=True)),
                ('match_quality', models.IntegerField(null=True)),
                ('dt_id', models.CharField(max_length=20, null=True)),
                ('date_mod', models.DateTimeField(auto_now=True)),
                ('times_validated', models.IntegerField(default=0)),
                ('note', models.CharField(max_length=200, null=True)),
                ('added_by', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='InSituExpt',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('imageseriesid', models.IntegerField()),
                ('plane', models.CharField(max_length=20)),
                ('valid', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Institution',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('type', models.CharField(max_length=50, null=True, choices=[(b'edu', b'University'), (b'org', b'Institute'), (b'com', b'Industry'), (b'gov', b'Government')])),
                ('country', models.CharField(max_length=50, null=True, choices=[(b'AF', 'Afghanistan'), (b'AX', 'Aland Islands'), (b'AL', 'Albania'), (b'DZ', 'Algeria'), (b'AS', 'American Samoa'), (b'AD', 'Andorra'), (b'AO', 'Angola'), (b'AI', 'Anguilla'), (b'AQ', 'Antarctica'), (b'AG', 'Antigua and Barbuda'), (b'AR', 'Argentina'), (b'AM', 'Armenia'), (b'AW', 'Aruba'), (b'AU', 'Australia'), (b'AT', 'Austria'), (b'AZ', 'Azerbaijan'), (b'BS', 'Bahamas'), (b'BH', 'Bahrain'), (b'BD', 'Bangladesh'), (b'BB', 'Barbados'), (b'BY', 'Belarus'), (b'BE', 'Belgium'), (b'BZ', 'Belize'), (b'BJ', 'Benin'), (b'BM', 'Bermuda'), (b'BT', 'Bhutan'), (b'BO', 'Bolivia'), (b'BA', 'Bosnia and Herzegovina'), (b'BW', 'Botswana'), (b'BV', 'Bouvet Island'), (b'BR', 'Brazil'), (b'IO', 'British Indian Ocean Territory'), (b'BN', 'Brunei Darussalam'), (b'BG', 'Bulgaria'), (b'BF', 'Burkina Faso'), (b'BI', 'Burundi'), (b'KH', 'Cambodia'), (b'CM', 'Cameroon'), (b'CA', 'Canada'), (b'CV', 'Cape Verde'), (b'KY', 'Cayman Islands'), (b'CF', 'Central African Republic'), (b'TD', 'Chad'), (b'CL', 'Chile'), (b'CN', 'China'), (b'CX', 'Christmas Island'), (b'CC', 'Cocos (Keeling) Islands'), (b'CO', 'Colombia'), (b'KM', 'Comoros'), (b'CG', 'Congo'), (b'CD', 'Congo, the Democratic Republic of the'), (b'CK', 'Cook Islands'), (b'CR', 'Costa Rica'), (b'CI', "Cote d'Ivoire"), (b'HR', 'Croatia'), (b'CU', 'Cuba'), (b'CY', 'Cyprus'), (b'CZ', 'Czech Republic'), (b'DK', 'Denmark'), (b'DJ', 'Djibouti'), (b'DM', 'Dominica'), (b'DO', 'Dominican Republic'), (b'EC', 'Ecuador'), (b'EG', 'Egypt'), (b'SV', 'El Salvador'), (b'GQ', 'Equatorial Guinea'), (b'ER', 'Eritrea'), (b'EE', 'Estonia'), (b'ET', 'Ethiopia'), (b'FK', 'Falkland Islands (Malvinas)'), (b'FO', 'Faroe Islands'), (b'FJ', 'Fiji'), (b'FI', 'Finland'), (b'FR', 'France'), (b'FX', 'France, Metropolitan'), (b'GF', 'French Guiana'), (b'PF', 'French Polynesia'), (b'TF', 'French Southern Territories'), (b'GA', 'Gabon'), (b'GM', 'Gambia'), (b'GE', 'Georgia'), (b'DE', 'Germany'), (b'GH', 'Ghana'), (b'GI', 'Gibraltar'), (b'GR', 'Greece'), (b'GL', 'Greenland'), (b'GD', 'Grenada'), (b'GP', 'Guadeloupe'), (b'GU', 'Guam'), (b'GT', 'Guatemala'), (b'GG', 'Guernsey'), (b'GN', 'Guinea'), (b'GW', 'Guinea-Bissau'), (b'GY', 'Guyana'), (b'HT', 'Haiti'), (b'HM', 'Heard Island and McDonald Islands'), (b'VA', 'Holy See (Vatican City State)'), (b'HN', 'Honduras'), (b'HK', 'Hong Kong'), (b'HU', 'Hungary'), (b'IS', 'Iceland'), (b'IN', 'India'), (b'ID', 'Indonesia'), (b'IR', 'Iran, Islamic Republic of'), (b'IQ', 'Iraq'), (b'IE', 'Ireland'), (b'IM', 'Isle of Man'), (b'IL', 'Israel'), (b'IT', 'Italy'), (b'JM', 'Jamaica'), (b'JP', 'Japan'), (b'JE', 'Jersey'), (b'JO', 'Jordan'), (b'KZ', 'Kazakhstan'), (b'KE', 'Kenya'), (b'KI', 'Kiribati'), (b'KP', "Korea, Democratic People's Republic of"), (b'KR', 'Korea, Republic of'), (b'KW', 'Kuwait'), (b'KG', 'Kyrgyzstan'), (b'LA', "Lao People's Democratic Republic"), (b'LV', 'Latvia'), (b'LB', 'Lebanon'), (b'LS', 'Lesotho'), (b'LR', 'Liberia'), (b'LY', 'Libyan Arab Jamahiriya'), (b'LI', 'Liechtenstein'), (b'LT', 'Lithuania'), (b'LU', 'Luxembourg'), (b'MO', 'Macao'), (b'MK', 'Macedonia, the former Yugoslav Republic of'), (b'MG', 'Madagascar'), (b'MW', 'Malawi'), (b'MY', 'Malaysia'), (b'MV', 'Maldives'), (b'ML', 'Mali'), (b'MT', 'Malta'), (b'MH', 'Marshall Islands'), (b'MQ', 'Martinique'), (b'MR', 'Mauritania'), (b'MU', 'Mauritius'), (b'YT', 'Mayotte'), (b'MX', 'Mexico'), (b'FM', 'Micronesia, Federated States of'), (b'MD', 'Moldova, Republic of'), (b'MC', 'Monaco'), (b'MN', 'Mongolia'), (b'ME', 'Montenegro'), (b'MS', 'Montserrat'), (b'MA', 'Morocco'), (b'MZ', 'Mozambique'), (b'MM', 'Myanmar'), (b'NA', 'Namibia'), (b'NR', 'Nauru'), (b'NP', 'Nepal'), (b'NL', 'Netherlands'), (b'AN', 'Netherlands Antilles'), (b'NC', 'New Caledonia'), (b'NZ', 'New Zealand'), (b'NI', 'Nicaragua'), (b'NE', 'Niger'), (b'NG', 'Nigeria'), (b'NU', 'Niue'), (b'NF', 'Norfolk Island'), (b'MP', 'Northern Mariana Islands'), (b'NO', 'Norway'), (b'OM', 'Oman'), (b'PK', 'Pakistan'), (b'PW', 'Palau'), (b'PS', 'Palestinian Territory, Occupied'), (b'PA', 'Panama'), (b'PG', 'Papua New Guinea'), (b'PY', 'Paraguay'), (b'PE', 'Peru'), (b'PH', 'Philippines'), (b'PN', 'Pitcairn'), (b'PL', 'Poland'), (b'PT', 'Portugal'), (b'PR', 'Puerto Rico'), (b'QA', 'Qatar'), (b'RE', 'Reunion'), (b'RO', 'Romania'), (b'RU', 'Russian Federation'), (b'RW', 'Rwanda'), (b'SH', 'Saint Helena'), (b'KN', 'Saint Kitts and Nevis'), (b'LC', 'Saint Lucia'), (b'PM', 'Saint Pierre and Miquelon'), (b'VC', 'Saint Vincent and the Grenadines'), (b'WS', 'Samoa'), (b'SM', 'San Marino'), (b'ST', 'Sao Tome and Principe'), (b'SA', 'Saudi Arabia'), (b'SN', 'Senegal'), (b'RS', 'Serbia'), (b'SC', 'Seychelles'), (b'SL', 'Sierra Leone'), (b'SG', 'Singapore'), (b'SK', 'Slovakia'), (b'SI', 'Slovenia'), (b'SB', 'Solomon Islands'), (b'SO', 'Somalia'), (b'ZA', 'South Africa'), (b'GS', 'South Georgia and the South Sandwich Islands'), (b'ES', 'Spain'), (b'LK', 'Sri Lanka'), (b'SD', 'Sudan'), (b'SR', 'Suriname'), (b'SJ', 'Svalbard and Jan Mayen'), (b'SZ', 'Swaziland'), (b'SE', 'Sweden'), (b'CH', 'Switzerland'), (b'SY', 'Syrian Arab Republic'), (b'TW', 'Taiwan, Province of China'), (b'TJ', 'Tajikistan'), (b'TZ', 'Tanzania, United Republic of'), (b'TH', 'Thailand'), (b'TL', 'Timor-Leste'), (b'TG', 'Togo'), (b'TK', 'Tokelau'), (b'TO', 'Tonga'), (b'TT', 'Trinidad and Tobago'), (b'TN', 'Tunisia'), (b'TR', 'Turkey'), (b'TM', 'Turkmenistan'), (b'TC', 'Turks and Caicos Islands'), (b'TV', 'Tuvalu'), (b'UG', 'Uganda'), (b'UA', 'Ukraine'), (b'AE', 'United Arab Emirates'), (b'GB', 'United Kingdom'), (b'US', 'United States'), (b'UM', 'United States Minor Outlying Islands'), (b'UY', 'Uruguay'), (b'UZ', 'Uzbekistan'), (b'VU', 'Vanuatu'), (b'VE', 'Venezuela'), (b'VN', 'Viet Nam'), (b'VG', 'Virgin Islands, British'), (b'VI', 'Virgin Islands, U.S.'), (b'WF', 'Wallis and Futuna'), (b'EH', 'Western Sahara'), (b'YE', 'Yemen'), (b'YU', 'Yugoslavia'), (b'ZM', 'Zambia'), (b'ZW', 'Zimbabwe'), (b'ZZ', 'Unknown or unspecified country')])),
                ('state', models.CharField(max_length=2, null=True, choices=[(b'AL', b'Alabama'), (b'AK', b'Alaska'), (b'AS', b'American Samoa'), (b'AZ', b'Arizona'), (b'AR', b'Arkansas'), (b'AA', b'Armed Forces Americas'), (b'AE', b'Armed Forces Europe'), (b'AP', b'Armed Forces Pacific'), (b'CA', b'California'), (b'CO', b'Colorado'), (b'CT', b'Connecticut'), (b'DE', b'Delaware'), (b'DC', b'District of Columbia'), (b'FL', b'Florida'), (b'GA', b'Georgia'), (b'GU', b'Guam'), (b'HI', b'Hawaii'), (b'ID', b'Idaho'), (b'IL', b'Illinois'), (b'IN', b'Indiana'), (b'IA', b'Iowa'), (b'KS', b'Kansas'), (b'KY', b'Kentucky'), (b'LA', b'Louisiana'), (b'ME', b'Maine'), (b'MD', b'Maryland'), (b'MA', b'Massachusetts'), (b'MI', b'Michigan'), (b'MN', b'Minnesota'), (b'MS', b'Mississippi'), (b'MO', b'Missouri'), (b'MT', b'Montana'), (b'NE', b'Nebraska'), (b'NV', b'Nevada'), (b'NH', b'New Hampshire'), (b'NJ', b'New Jersey'), (b'NM', b'New Mexico'), (b'NY', b'New York'), (b'NC', b'North Carolina'), (b'ND', b'North Dakota'), (b'MP', b'Northern Mariana Islands'), (b'OH', b'Ohio'), (b'OK', b'Oklahoma'), (b'OR', b'Oregon'), (b'PA', b'Pennsylvania'), (b'PR', b'Puerto Rico'), (b'RI', b'Rhode Island'), (b'SC', b'South Carolina'), (b'SD', b'South Dakota'), (b'TN', b'Tennessee'), (b'TX', b'Texas'), (b'UT', b'Utah'), (b'VT', b'Vermont'), (b'VI', b'Virgin Islands'), (b'VA', b'Virginia'), (b'WA', b'Washington'), (b'WV', b'West Virginia'), (b'WI', b'Wisconsin'), (b'WY', b'Wyoming')])),
            ],
        ),
        migrations.CreateModel(
            name='Journal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=300)),
                ('short_title', models.CharField(max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='MailingListEntry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email', models.EmailField(max_length=254)),
                ('name', models.CharField(max_length=200, null=True)),
                ('comments', models.CharField(max_length=500, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='MeshTerm',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('term', models.CharField(max_length=300)),
            ],
        ),
        migrations.CreateModel(
            name='MetaData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('value', models.CharField(max_length=100, null=True)),
                ('cont_value', models.ForeignKey(to='neuroelectro.ContValue', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Neuron',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=500)),
                ('nlex_id', models.CharField(max_length=100, null=True)),
                ('neuron_db_id', models.IntegerField(null=True)),
                ('date_mod', models.DateTimeField(auto_now=True, null=True)),
                ('added_by', models.CharField(max_length=20, null=True)),
                ('regions', models.ManyToManyField(to='neuroelectro.BrainRegion', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='NeuronArticleMap',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('num_mentions', models.IntegerField(null=True)),
                ('date_mod', models.DateTimeField(auto_now=True)),
                ('added_by', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True)),
                ('article', models.ForeignKey(to='neuroelectro.Article', null=True)),
                ('neuron', models.ForeignKey(to='neuroelectro.Neuron')),
            ],
        ),
        migrations.CreateModel(
            name='NeuronConceptMap',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ref_text', models.CharField(max_length=200, null=True)),
                ('match_quality', models.IntegerField(null=True)),
                ('dt_id', models.CharField(max_length=20, null=True)),
                ('date_mod', models.DateTimeField(auto_now=True)),
                ('times_validated', models.IntegerField(default=0)),
                ('note', models.CharField(max_length=200, null=True)),
                ('neuron_long_name', models.CharField(max_length=1000, null=True)),
                ('added_by', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True)),
                ('neuron', models.ForeignKey(to='neuroelectro.Neuron')),
                ('source', models.ForeignKey(to='neuroelectro.DataSource')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='NeuronData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('neuron_name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='NeuronDataAddMain',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('pubmed_id', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='NeuronEphysDataMap',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ref_text', models.CharField(max_length=200, null=True)),
                ('match_quality', models.IntegerField(null=True)),
                ('dt_id', models.CharField(max_length=20, null=True)),
                ('date_mod', models.DateTimeField(auto_now=True)),
                ('times_validated', models.IntegerField(default=0)),
                ('note', models.CharField(max_length=200, null=True)),
                ('val', models.FloatField()),
                ('err', models.FloatField(null=True)),
                ('n', models.IntegerField(null=True)),
                ('val_norm', models.FloatField(null=True)),
                ('norm_flag', models.BooleanField(default=False)),
                ('added_by', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True)),
                ('ephys_concept_map', models.ForeignKey(to='neuroelectro.EphysConceptMap')),
                ('exp_fact_concept_maps', models.ManyToManyField(to='neuroelectro.ExpFactConceptMap', null=True)),
                ('neuron_concept_map', models.ForeignKey(to='neuroelectro.NeuronConceptMap')),
                ('source', models.ForeignKey(to='neuroelectro.DataSource')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='NeuronEphysSummary',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('num_nedms', models.IntegerField(null=True)),
                ('date_mod', models.DateTimeField(auto_now=True)),
                ('data', models.TextField(default=b'')),
                ('num_articles', models.IntegerField(null=True)),
                ('value_mean', models.FloatField(null=True)),
                ('value_sd', models.FloatField(null=True)),
                ('ephys_prop', models.ForeignKey(to='neuroelectro.EphysProp')),
                ('neuron', models.ForeignKey(to='neuroelectro.Neuron')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='NeuronSummary',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('num_nedms', models.IntegerField(null=True)),
                ('date_mod', models.DateTimeField(auto_now=True)),
                ('data', models.TextField(default=b'')),
                ('num_articles', models.IntegerField(null=True)),
                ('num_ephysprops', models.IntegerField(null=True)),
                ('cluster_xval', models.FloatField(null=True)),
                ('cluster_yval', models.FloatField(null=True)),
                ('neuron', models.ForeignKey(to='neuroelectro.Neuron')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='NeuronSyn',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('term', models.CharField(max_length=500)),
            ],
        ),
        migrations.CreateModel(
            name='Protein',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('gene', models.CharField(max_length=20)),
                ('name', models.CharField(max_length=400)),
                ('common_name', models.CharField(max_length=400, null=True)),
                ('allenid', models.IntegerField()),
                ('entrezid', models.IntegerField(null=True)),
                ('is_channel', models.BooleanField(default=False)),
                ('in_situ_expts', models.ManyToManyField(to='neuroelectro.InSituExpt', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ProteinSyn',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('term', models.CharField(max_length=500)),
            ],
        ),
        migrations.CreateModel(
            name='Publisher',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='ReferenceText',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.CharField(max_length=3000)),
            ],
        ),
        migrations.CreateModel(
            name='RegionExpr',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('expr_energy', models.FloatField(null=True)),
                ('expr_density', models.FloatField(null=True)),
                ('expr_energy_cv', models.FloatField(null=True)),
                ('region', models.ForeignKey(default=0, to='neuroelectro.BrainRegion')),
            ],
        ),
        migrations.CreateModel(
            name='Species',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=500)),
            ],
        ),
        migrations.CreateModel(
            name='Substance',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('term', models.CharField(max_length=300)),
            ],
        ),
        migrations.CreateModel(
            name='Unit',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=20, choices=[(b'A', b'Amps'), (b'V', b'Volts'), (b'Ohms', '\u03a9'), (b'F', b'Farads'), (b's', b'Seconds'), (b'Hz', b'Hertz'), (b'm', b'Meters'), (b'ratio', b'Ratio')])),
                ('prefix', models.CharField(max_length=1, choices=[(b'f', b'f'), (b'p', b'p'), (b'u', '\u03bc'), (b'm', b'm'), (b'', b''), (b'k', b'k'), (b'M', b'M'), (b'G', b'G'), (b'T', b'T')])),
            ],
        ),
        migrations.CreateModel(
            name='UserSubmission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_mod', models.DateTimeField(auto_now=True)),
                ('data', picklefield.fields.PickledObjectField(null=True, editable=False)),
                ('article', models.ForeignKey(to='neuroelectro.Article', null=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='UserUpload',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_mod', models.DateTimeField(auto_now=True)),
                ('path', models.FilePathField()),
                ('data', picklefield.fields.PickledObjectField(null=True, editable=False)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='UserValidation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_mod', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='protein',
            name='synonyms',
            field=models.ManyToManyField(to='neuroelectro.ProteinSyn', null=True),
        ),
        migrations.AddField(
            model_name='neuronephysdatamap',
            name='validated_by',
            field=models.ManyToManyField(to='neuroelectro.UserValidation', null=True),
        ),
        migrations.AddField(
            model_name='neurondata',
            name='article_id',
            field=models.ForeignKey(to='neuroelectro.NeuronDataAddMain'),
        ),
        migrations.AddField(
            model_name='neuronconceptmap',
            name='validated_by',
            field=models.ManyToManyField(to='neuroelectro.UserValidation', null=True),
        ),
        migrations.AddField(
            model_name='neuron',
            name='synonyms',
            field=models.ManyToManyField(to='neuroelectro.NeuronSyn', null=True),
        ),
        migrations.AddField(
            model_name='metadata',
            name='ref_text',
            field=models.ForeignKey(to='neuroelectro.ReferenceText', null=True),
        ),
        migrations.AddField(
            model_name='journal',
            name='publisher',
            field=models.ForeignKey(to='neuroelectro.Publisher', null=True),
        ),
        migrations.AddField(
            model_name='insituexpt',
            name='regionexprs',
            field=models.ManyToManyField(to='neuroelectro.RegionExpr', null=True),
        ),
        migrations.AddField(
            model_name='expfactconceptmap',
            name='metadata',
            field=models.ForeignKey(to='neuroelectro.MetaData'),
        ),
        migrations.AddField(
            model_name='expfactconceptmap',
            name='source',
            field=models.ForeignKey(to='neuroelectro.DataSource'),
        ),
        migrations.AddField(
            model_name='expfactconceptmap',
            name='validated_by',
            field=models.ManyToManyField(to='neuroelectro.UserValidation', null=True),
        ),
        migrations.AddField(
            model_name='ephysproperty',
            name='neuron_id',
            field=models.ForeignKey(to='neuroelectro.NeuronData'),
        ),
        migrations.AddField(
            model_name='ephysprop',
            name='synonyms',
            field=models.ManyToManyField(to='neuroelectro.EphysPropSyn'),
        ),
        migrations.AddField(
            model_name='ephysprop',
            name='units',
            field=models.ForeignKey(to='neuroelectro.Unit', null=True),
        ),
        migrations.AddField(
            model_name='ephysconceptmap',
            name='ephys_prop',
            field=models.ForeignKey(to='neuroelectro.EphysProp'),
        ),
        migrations.AddField(
            model_name='ephysconceptmap',
            name='source',
            field=models.ForeignKey(to='neuroelectro.DataSource'),
        ),
        migrations.AddField(
            model_name='ephysconceptmap',
            name='validated_by',
            field=models.ManyToManyField(to='neuroelectro.UserValidation', null=True),
        ),
        migrations.AddField(
            model_name='datasource',
            name='data_table',
            field=models.ForeignKey(to='neuroelectro.DataTable', null=True),
        ),
        migrations.AddField(
            model_name='datasource',
            name='user_submission',
            field=models.ForeignKey(to='neuroelectro.UserSubmission', null=True),
        ),
        migrations.AddField(
            model_name='datasource',
            name='user_upload',
            field=models.ForeignKey(to='neuroelectro.UserUpload', null=True),
        ),
        migrations.AddField(
            model_name='articlemetadatamap',
            name='metadata',
            field=models.ForeignKey(to='neuroelectro.MetaData'),
        ),
        migrations.AddField(
            model_name='articlemetadatamap',
            name='validated_by',
            field=models.ManyToManyField(to='neuroelectro.UserValidation', null=True),
        ),
        migrations.AddField(
            model_name='article',
            name='authors',
            field=models.ManyToManyField(to='neuroelectro.Author', null=True),
        ),
        migrations.AddField(
            model_name='article',
            name='journal',
            field=models.ForeignKey(to='neuroelectro.Journal', null=True),
        ),
        migrations.AddField(
            model_name='article',
            name='substances',
            field=models.ManyToManyField(to='neuroelectro.Substance', null=True),
        ),
        migrations.AddField(
            model_name='article',
            name='terms',
            field=models.ManyToManyField(to='neuroelectro.MeshTerm', null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='assigned_neurons',
            field=models.ManyToManyField(to='neuroelectro.Neuron', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='user',
            name='groups',
            field=models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Group', blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', verbose_name='groups'),
        ),
        migrations.AddField(
            model_name='user',
            name='institution',
            field=models.ForeignKey(blank=True, to='neuroelectro.Institution', null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Permission', blank=True, help_text='Specific permissions for this user.', verbose_name='user permissions'),
        ),
    ]
