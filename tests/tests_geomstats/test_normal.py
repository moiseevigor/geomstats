"""Unit tests for the MultivariateDiagonalNormalDistributions manifold."""

from scipy.stats import multivariate_normal

import geomstats.backend as gs
from tests.conftest import Parametrizer, tf_backend
from tests.data.normal_data import (
    CenteredNormalDistributionsTestData,
    CenteredNormalMetricTestData,
    DiagonalNormalDistributionsTestData,
    DiagonalNormalMetricTestData,
    GeneralNormalDistributionsTestData,
)
from tests.geometry_test_cases import (
    ManifoldTestCase,
    OpenSetTestCase,
    RiemannianMetricTestCase,
)

TF_BACKEND = tf_backend()


class TestCenteredNormalDistributions(OpenSetTestCase, metaclass=Parametrizer):
    testing_data = CenteredNormalDistributionsTestData()
    skip_all = TF_BACKEND

    def test_belongs(self, sample_dim, point, expected):
        self.assertAllClose(self.Space(sample_dim).belongs(point), expected)

    def test_random_point_shape(self, point, expected):
        self.assertAllClose(point.shape, expected)

    def test_sample(self, sample_dim, point, n_samples, expected):
        self.assertAllClose(
            self.Space(sample_dim).sample(point, n_samples).shape, expected
        )

    def test_point_to_pdf(self, sample_dim, point, n_samples):
        space = self.Space(sample_dim)
        samples = space.sample(space.random_point(), n_samples)
        result = space.point_to_pdf(point)(samples)

        samples = gs.to_ndarray(samples, to_ndim=2, axis=0)
        point = gs.to_ndarray(point, to_ndim=3, axis=0)
        expected = []
        for i in range(point.shape[0]):
            tmp = list()
            mean, cov = gs.zeros(sample_dim), point[i]
            for j in range(samples.shape[0]):
                x = samples[j]
                tmp.append(multivariate_normal.pdf(x, mean=mean, cov=cov))
            expected.append(gs.array(tmp))
        expected = gs.transpose(gs.squeeze(gs.stack(expected, axis=0)))
        self.assertAllClose(result, expected)


class TestDiagonalNormalDistributions(OpenSetTestCase, metaclass=Parametrizer):
    testing_data = DiagonalNormalDistributionsTestData()
    skip_all = TF_BACKEND

    def test_belongs(self, sample_dim, point, expected):
        self.assertAllClose(self.Space(sample_dim).belongs(point), expected)

    def test_random_point_shape(self, point, expected):
        self.assertAllClose(point.shape, expected)

    def test_sample(self, sample_dim, point, n_samples, expected):
        self.assertAllClose(
            self.Space(sample_dim).sample(point, n_samples).shape, expected
        )

    def test_point_to_pdf(self, sample_dim, point, n_samples):
        space = self.Space(sample_dim)
        samples = space.sample(space.random_point(), n_samples)
        result = space.point_to_pdf(point)(samples)

        samples = gs.to_ndarray(samples, to_ndim=2, axis=0)
        point = gs.to_ndarray(point, to_ndim=2, axis=0)
        expected = []
        for i in range(point.shape[0]):
            mean, cov = space._unstack_mean_diagonal(sample_dim, point[i, ...])
            tmp = list()
            for j in range(samples.shape[0]):
                x = samples[j, ...]
                tmp.append(multivariate_normal.pdf(x, mean=mean, cov=cov))
            expected.append(gs.array(tmp))
        expected = gs.squeeze(gs.stack(expected, axis=0))
        self.assertAllClose(result, expected)


class TestGeneralNormalDistributions(ManifoldTestCase, metaclass=Parametrizer):
    testing_data = GeneralNormalDistributionsTestData()
    skip_all = TF_BACKEND

    def test_unstack_mean_covariance(
        self, sample_dim, point, mean_expected, cov_expected
    ):
        mean, cov = self.Space(sample_dim)._unstack_mean_covariance(point)
        self.assertAllClose(mean.shape, mean_expected)
        self.assertAllClose(cov.shape, cov_expected)

    def test_belongs(self, sample_dim, point, expected):
        self.assertAllClose(self.Space(sample_dim).belongs(point), expected)

    def test_random_point_shape(self, point, expected):
        self.assertAllClose(point.shape, expected)

    def test_sample(self, sample_dim, point, n_samples, expected):
        self.assertAllClose(
            self.Space(sample_dim).sample(point, n_samples).shape, expected
        )

    def test_point_to_pdf(self, sample_dim, point, n_samples):
        space = self.Space(sample_dim)
        samples = space.sample(space.random_point(), n_samples)
        result = space.point_to_pdf(point)(samples)

        samples = gs.to_ndarray(samples, to_ndim=2, axis=0)
        point = gs.to_ndarray(point, to_ndim=2, axis=0)
        expected = []
        for i in range(point.shape[0]):
            tmp = list()
            mean, cov = space._unstack_mean_covariance(point[i])
            for j in range(samples.shape[0]):
                x = samples[j]
                tmp.append(multivariate_normal.pdf(x, mean=mean, cov=cov))
            expected.append(gs.array(tmp))
        expected = gs.transpose(gs.squeeze(gs.stack(expected, axis=0)))
        self.assertAllClose(result, expected)


class TestCenteredNormalMetric(RiemannianMetricTestCase, metaclass=Parametrizer):
    skip_test_parallel_transport_ivp_is_isometry = True
    skip_test_parallel_transport_bvp_is_isometry = True
    skip_test_geodesic_ivp_belongs = True
    skip_test_geodesic_bvp_belongs = True
    skip_test_exp_geodesic_ivp = True
    skip_test_exp_ladder_parallel_transport = True
    skip_test_riemann_tensor_shape = True
    skip_test_ricci_tensor_shape = True
    skip_test_scalar_curvature_shape = True
    skip_test_covariant_riemann_tensor_is_skew_symmetric_1 = True
    skip_test_covariant_riemann_tensor_is_skew_symmetric_2 = True
    skip_test_covariant_riemann_tensor_bianchi_identity = True
    skip_test_covariant_riemann_tensor_is_interchange_symmetric = True
    skip_test_sectional_curvature_shape = True
    skip_all = TF_BACKEND

    testing_data = CenteredNormalMetricTestData()
    Space = testing_data.Space

    def test_inner_product_shape(
        self, metric, tangent_vec_a, tangent_vec_b, base_point, expected
    ):
        result = metric.inner_product(tangent_vec_a, tangent_vec_b, base_point)
        result = result.shape
        self.assertAllClose(result, expected)

    def test_log_after_exp(self, connection_args, tangent_vec, base_point, rtol, atol):
        connection = self.Metric(*connection_args)
        exp = connection.exp(tangent_vec=tangent_vec, base_point=gs.array(base_point))
        result = connection.log(exp, base_point=gs.array(base_point))
        self.assertAllClose(result, gs.squeeze(tangent_vec), rtol=rtol, atol=atol)

    def test_dist(self, metric, point_a, point_b, expected):
        result = metric.dist(point_a, point_b)
        self.assertAllClose(result, expected)


class TestDiagonalNormalMetric(RiemannianMetricTestCase, metaclass=Parametrizer):
    skip_test_parallel_transport_ivp_is_isometry = True
    skip_test_parallel_transport_bvp_is_isometry = True
    skip_test_geodesic_ivp_belongs = True
    skip_test_geodesic_bvp_belongs = True
    skip_test_exp_geodesic_ivp = True
    skip_test_exp_ladder_parallel_transport = True
    skip_test_riemann_tensor_shape = True
    skip_test_ricci_tensor_shape = True
    skip_test_scalar_curvature_shape = True
    skip_test_covariant_riemann_tensor_is_skew_symmetric_1 = True
    skip_test_covariant_riemann_tensor_is_skew_symmetric_2 = True
    skip_test_covariant_riemann_tensor_bianchi_identity = True
    skip_test_covariant_riemann_tensor_is_interchange_symmetric = True
    skip_test_sectional_curvature_shape = True
    skip_all = TF_BACKEND

    testing_data = DiagonalNormalMetricTestData()
    Space = testing_data.Space

    def test_inner_product_shape(
        self, metric, tangent_vec_a, tangent_vec_b, base_point, expected
    ):
        result = metric.inner_product(tangent_vec_a, tangent_vec_b, base_point)
        result = result.shape
        self.assertAllClose(result, expected)
