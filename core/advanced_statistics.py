"""
Advanced Statistical Tests Module
Additional statistical tests beyond the basic ones in data_analysis.py
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Union
from scipy import stats
from scipy.stats import (
    # Non-parametric tests
    mannwhitneyu, kruskal, wilcoxon, friedmanchisquare,
    # Variance tests
    levene, bartlett, fligner,
    # Normality tests
    shapiro, normaltest, anderson, jarque_bera, kstest,
    # Post-hoc tests
    tukey_hsd,
    # Effect sizes
    spearmanr, kendalltau,
    # Distribution tests
    ks_2samp, epps_singleton_2samp
)
import warnings
warnings.filterwarnings('ignore')


class AdvancedStatisticalTests:
    """
    Advanced statistical hypothesis testing.
    """

    @staticmethod
    def mann_whitney_u_test(
        group1: Union[pd.Series, np.ndarray],
        group2: Union[pd.Series, np.ndarray],
        alternative: str = 'two-sided'
    ) -> Dict[str, Any]:
        """
        Mann-Whitney U test (non-parametric alternative to t-test).

        Args:
            group1: First group data
            group2: Second group data
            alternative: 'two-sided', 'less', or 'greater'

        Returns:
            Test results
        """
        # Remove NaN values
        group1_clean = pd.Series(group1).dropna()
        group2_clean = pd.Series(group2).dropna()

        # Perform test
        statistic, p_value = mannwhitneyu(
            group1_clean,
            group2_clean,
            alternative=alternative
        )

        # Effect size (rank-biserial correlation)
        n1, n2 = len(group1_clean), len(group2_clean)
        effect_size = 1 - (2 * statistic) / (n1 * n2)

        return {
            'test': 'Mann-Whitney U Test',
            'statistic': float(statistic),
            'p_value': float(p_value),
            'effect_size': float(effect_size),
            'alternative': alternative,
            'n_group1': n1,
            'n_group2': n2,
            'significant': p_value < 0.05,
            'interpretation': 'Groups are significantly different' if p_value < 0.05 else 'No significant difference'
        }

    @staticmethod
    def kruskal_wallis_test(
        *groups: Union[pd.Series, np.ndarray]
    ) -> Dict[str, Any]:
        """
        Kruskal-Wallis H-test (non-parametric alternative to one-way ANOVA).

        Args:
            *groups: Variable number of group data

        Returns:
            Test results
        """
        # Clean groups
        cleaned_groups = [pd.Series(g).dropna() for g in groups]

        # Perform test
        statistic, p_value = kruskal(*cleaned_groups)

        # Effect size (eta-squared)
        n_total = sum(len(g) for g in cleaned_groups)
        k = len(cleaned_groups)
        eta_squared = (statistic - k + 1) / (n_total - k)

        return {
            'test': 'Kruskal-Wallis H Test',
            'statistic': float(statistic),
            'p_value': float(p_value),
            'effect_size_eta_squared': float(eta_squared),
            'n_groups': k,
            'group_sizes': [len(g) for g in cleaned_groups],
            'significant': p_value < 0.05,
            'interpretation': 'At least one group differs' if p_value < 0.05 else 'No significant difference between groups'
        }

    @staticmethod
    def wilcoxon_signed_rank_test(
        group1: Union[pd.Series, np.ndarray],
        group2: Union[pd.Series, np.ndarray],
        alternative: str = 'two-sided'
    ) -> Dict[str, Any]:
        """
        Wilcoxon signed-rank test (paired non-parametric test).

        Args:
            group1: First paired group
            group2: Second paired group
            alternative: 'two-sided', 'less', or 'greater'

        Returns:
            Test results
        """
        # Remove NaN values (paired)
        df = pd.DataFrame({'g1': group1, 'g2': group2}).dropna()

        # Perform test
        statistic, p_value = wilcoxon(
            df['g1'],
            df['g2'],
            alternative=alternative
        )

        return {
            'test': 'Wilcoxon Signed-Rank Test',
            'statistic': float(statistic),
            'p_value': float(p_value),
            'alternative': alternative,
            'n_pairs': len(df),
            'significant': p_value < 0.05,
            'interpretation': 'Paired groups are significantly different' if p_value < 0.05 else 'No significant difference'
        }

    @staticmethod
    def levene_test(
        *groups: Union[pd.Series, np.ndarray],
        center: str = 'median'
    ) -> Dict[str, Any]:
        """
        Levene's test for equality of variances.

        Args:
            *groups: Variable number of group data
            center: 'mean', 'median', or 'trimmed'

        Returns:
            Test results
        """
        # Clean groups
        cleaned_groups = [pd.Series(g).dropna() for g in groups]

        # Perform test
        statistic, p_value = levene(*cleaned_groups, center=center)

        return {
            'test': "Levene's Test for Equal Variances",
            'statistic': float(statistic),
            'p_value': float(p_value),
            'center': center,
            'n_groups': len(cleaned_groups),
            'group_variances': [float(g.var()) for g in cleaned_groups],
            'significant': p_value < 0.05,
            'equal_variances': p_value >= 0.05,
            'interpretation': 'Variances are NOT equal' if p_value < 0.05 else 'Variances are equal'
        }

    @staticmethod
    def bartlett_test(
        *groups: Union[pd.Series, np.ndarray]
    ) -> Dict[str, Any]:
        """
        Bartlett's test for equality of variances (assumes normality).

        Args:
            *groups: Variable number of group data

        Returns:
            Test results
        """
        # Clean groups
        cleaned_groups = [pd.Series(g).dropna() for g in groups]

        # Perform test
        statistic, p_value = bartlett(*cleaned_groups)

        return {
            'test': "Bartlett's Test for Equal Variances",
            'statistic': float(statistic),
            'p_value': float(p_value),
            'n_groups': len(cleaned_groups),
            'group_variances': [float(g.var()) for g in cleaned_groups],
            'significant': p_value < 0.05,
            'equal_variances': p_value >= 0.05,
            'interpretation': 'Variances are NOT equal' if p_value < 0.05 else 'Variances are equal',
            'note': 'Assumes normally distributed data. Use Levene test if normality is questionable.'
        }

    @staticmethod
    def comprehensive_normality_test(
        data: Union[pd.Series, np.ndarray]
    ) -> Dict[str, Any]:
        """
        Comprehensive normality testing with multiple tests.

        Args:
            data: Data to test for normality

        Returns:
            Results from multiple normality tests
        """
        data_clean = pd.Series(data).dropna()

        results = {
            'sample_size': len(data_clean),
            'tests': {}
        }

        # Shapiro-Wilk test (best for small samples)
        if len(data_clean) >= 3:
            try:
                stat, p = shapiro(data_clean)
                results['tests']['shapiro_wilk'] = {
                    'statistic': float(stat),
                    'p_value': float(p),
                    'is_normal': p >= 0.05
                }
            except:
                pass

        # D'Agostino-Pearson test
        if len(data_clean) >= 8:
            try:
                stat, p = normaltest(data_clean)
                results['tests']['dagostino_pearson'] = {
                    'statistic': float(stat),
                    'p_value': float(p),
                    'is_normal': p >= 0.05
                }
            except:
                pass

        # Anderson-Darling test
        try:
            result = anderson(data_clean)
            results['tests']['anderson_darling'] = {
                'statistic': float(result.statistic),
                'critical_values': result.critical_values.tolist(),
                'significance_levels': result.significance_level.tolist(),
                'is_normal': result.statistic < result.critical_values[2]  # 5% significance
            }
        except:
            pass

        # Jarque-Bera test
        try:
            stat, p = jarque_bera(data_clean)
            results['tests']['jarque_bera'] = {
                'statistic': float(stat),
                'p_value': float(p),
                'is_normal': p >= 0.05
            }
        except:
            pass

        # Kolmogorov-Smirnov test (against normal distribution)
        try:
            mean, std = data_clean.mean(), data_clean.std()
            stat, p = kstest(data_clean, 'norm', args=(mean, std))
            results['tests']['kolmogorov_smirnov'] = {
                'statistic': float(stat),
                'p_value': float(p),
                'is_normal': p >= 0.05
            }
        except:
            pass

        # Consensus
        normal_count = sum(1 for test in results['tests'].values() if test.get('is_normal', False))
        total_tests = len(results['tests'])

        results['consensus'] = {
            'tests_indicating_normal': normal_count,
            'total_tests': total_tests,
            'majority_normal': normal_count > total_tests / 2,
            'recommendation': 'Data appears normally distributed' if normal_count > total_tests / 2 else 'Data does NOT appear normally distributed'
        }

        # Descriptive statistics
        results['descriptive'] = {
            'mean': float(data_clean.mean()),
            'median': float(data_clean.median()),
            'std': float(data_clean.std()),
            'skewness': float(stats.skew(data_clean)),
            'kurtosis': float(stats.kurtosis(data_clean))
        }

        return results

    @staticmethod
    def paired_t_test(
        group1: Union[pd.Series, np.ndarray],
        group2: Union[pd.Series, np.ndarray],
        alternative: str = 'two-sided'
    ) -> Dict[str, Any]:
        """
        Paired t-test for dependent samples.

        Args:
            group1: First paired group
            group2: Second paired group
            alternative: 'two-sided', 'less', or 'greater'

        Returns:
            Test results
        """
        # Remove NaN values (paired)
        df = pd.DataFrame({'g1': group1, 'g2': group2}).dropna()

        # Perform paired t-test
        statistic, p_value = stats.ttest_rel(
            df['g1'],
            df['g2'],
            alternative=alternative
        )

        # Calculate effect size (Cohen's d for paired samples)
        differences = df['g1'] - df['g2']
        cohen_d = differences.mean() / differences.std()

        return {
            'test': 'Paired t-Test',
            'statistic': float(statistic),
            'p_value': float(p_value),
            'cohens_d': float(cohen_d),
            'alternative': alternative,
            'n_pairs': len(df),
            'mean_difference': float(differences.mean()),
            'std_difference': float(differences.std()),
            'significant': p_value < 0.05,
            'interpretation': 'Paired groups are significantly different' if p_value < 0.05 else 'No significant difference'
        }

    @staticmethod
    def post_hoc_tukey(
        data: pd.DataFrame,
        value_column: str,
        group_column: str
    ) -> Dict[str, Any]:
        """
        Tukey's HSD post-hoc test for pairwise comparisons.

        Args:
            data: DataFrame containing data
            value_column: Name of value column
            group_column: Name of group column

        Returns:
            Pairwise comparison results
        """
        try:
            from statsmodels.stats.multicomp import pairwise_tukeyhsd

            # Perform Tukey HSD
            tukey = pairwise_tukeyhsd(
                endog=data[value_column],
                groups=data[group_column],
                alpha=0.05
            )

            # Parse results
            results_df = pd.DataFrame(data=tukey.summary().data[1:], columns=tukey.summary().data[0])

            return {
                'test': "Tukey's HSD Post-Hoc Test",
                'pairwise_comparisons': results_df.to_dict('records'),
                'summary': str(tukey),
                'significant_pairs': results_df[results_df['reject'] == True].to_dict('records') if 'reject' in results_df.columns else []
            }

        except ImportError:
            return {
                'error': 'statsmodels not installed. Install with: pip install statsmodels',
                'install_command': 'pip install statsmodels'
            }
        except Exception as e:
            return {'error': str(e)}

    @staticmethod
    def kolmogorov_smirnov_2sample(
        sample1: Union[pd.Series, np.ndarray],
        sample2: Union[pd.Series, np.ndarray],
        alternative: str = 'two-sided'
    ) -> Dict[str, Any]:
        """
        Two-sample Kolmogorov-Smirnov test.

        Args:
            sample1: First sample
            sample2: Second sample
            alternative: 'two-sided', 'less', or 'greater'

        Returns:
            Test results
        """
        # Clean data
        s1 = pd.Series(sample1).dropna()
        s2 = pd.Series(sample2).dropna()

        # Perform test
        statistic, p_value = ks_2samp(s1, s2, alternative=alternative)

        return {
            'test': 'Two-Sample Kolmogorov-Smirnov Test',
            'statistic': float(statistic),
            'p_value': float(p_value),
            'alternative': alternative,
            'n_sample1': len(s1),
            'n_sample2': len(s2),
            'significant': p_value < 0.05,
            'interpretation': 'Samples come from different distributions' if p_value < 0.05 else 'Samples likely from same distribution'
        }

    @staticmethod
    def effect_size_cohens_d(
        group1: Union[pd.Series, np.ndarray],
        group2: Union[pd.Series, np.ndarray]
    ) -> Dict[str, Any]:
        """
        Calculate Cohen's d effect size.

        Args:
            group1: First group
            group2: Second group

        Returns:
            Effect size and interpretation
        """
        # Clean data
        g1 = pd.Series(group1).dropna()
        g2 = pd.Series(group2).dropna()

        # Calculate pooled standard deviation
        n1, n2 = len(g1), len(g2)
        var1, var2 = g1.var(), g2.var()
        pooled_std = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))

        # Calculate Cohen's d
        cohens_d = (g1.mean() - g2.mean()) / pooled_std

        # Interpretation
        if abs(cohens_d) < 0.2:
            interpretation = 'negligible'
        elif abs(cohens_d) < 0.5:
            interpretation = 'small'
        elif abs(cohens_d) < 0.8:
            interpretation = 'medium'
        else:
            interpretation = 'large'

        return {
            'cohens_d': float(cohens_d),
            'effect_size': interpretation,
            'group1_mean': float(g1.mean()),
            'group2_mean': float(g2.mean()),
            'mean_difference': float(g1.mean() - g2.mean()),
            'pooled_std': float(pooled_std),
            'n_group1': n1,
            'n_group2': n2
        }

    @staticmethod
    def cramers_v(
        df: pd.DataFrame,
        col1: str,
        col2: str
    ) -> Dict[str, Any]:
        """
        Calculate Cramér's V effect size for categorical association.

        Args:
            df: DataFrame
            col1: First categorical column
            col2: Second categorical column

        Returns:
            Cramér's V and interpretation
        """
        # Create contingency table
        contingency = pd.crosstab(df[col1], df[col2])

        # Chi-square test
        chi2, p_value, dof, expected = stats.chi2_contingency(contingency)

        # Calculate Cramér's V
        n = contingency.sum().sum()
        min_dim = min(contingency.shape[0] - 1, contingency.shape[1] - 1)
        cramers_v = np.sqrt(chi2 / (n * min_dim))

        # Interpretation
        if cramers_v < 0.1:
            interpretation = 'negligible'
        elif cramers_v < 0.3:
            interpretation = 'weak'
        elif cramers_v < 0.5:
            interpretation = 'moderate'
        else:
            interpretation = 'strong'

        return {
            'cramers_v': float(cramers_v),
            'effect_size': interpretation,
            'chi_square': float(chi2),
            'p_value': float(p_value),
            'significant': p_value < 0.05,
            'sample_size': int(n)
        }

    @staticmethod
    def friedman_test(
        *groups: Union[pd.Series, np.ndarray]
    ) -> Dict[str, Any]:
        """
        Friedman test (non-parametric repeated measures ANOVA).

        Args:
            *groups: Variable number of related group data

        Returns:
            Test results
        """
        # Clean and align groups
        cleaned_groups = [pd.Series(g).dropna() for g in groups]

        # Perform test
        statistic, p_value = friedmanchisquare(*cleaned_groups)

        return {
            'test': 'Friedman Test',
            'statistic': float(statistic),
            'p_value': float(p_value),
            'n_groups': len(cleaned_groups),
            'group_sizes': [len(g) for g in cleaned_groups],
            'significant': p_value < 0.05,
            'interpretation': 'At least one group differs (repeated measures)' if p_value < 0.05 else 'No significant difference'
        }


def power_analysis_ttest(
    effect_size: float,
    alpha: float = 0.05,
    power: float = 0.8,
    alternative: str = 'two-sided'
) -> Dict[str, Any]:
    """
    Statistical power analysis for t-test.
    Note: Requires statsmodels.

    Args:
        effect_size: Expected effect size (Cohen's d)
        alpha: Significance level
        power: Desired statistical power
        alternative: 'two-sided' or 'one-sided'

    Returns:
        Required sample size and power analysis
    """
    try:
        from statsmodels.stats.power import ttest_power

        # Calculate required sample size
        required_n = ttest_power(
            effect_size=effect_size,
            nobs=None,
            alpha=alpha,
            power=power,
            alternative=alternative
        )

        return {
            'required_sample_size_per_group': int(np.ceil(required_n)),
            'effect_size': effect_size,
            'alpha': alpha,
            'power': power,
            'alternative': alternative,
            'interpretation': f'Need at least {int(np.ceil(required_n))} samples per group to detect effect size of {effect_size} with {power*100}% power'
        }

    except ImportError:
        return {
            'error': 'statsmodels not installed. Install with: pip install statsmodels',
            'install_command': 'pip install statsmodels'
        }
    except Exception as e:
        return {'error': str(e)}
