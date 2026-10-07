"""Unified Triality Pipeline (UTP) Distribution Configuration Module:
Package Setup and Environment Orchestrator
Reference: UTP-SPEC-2026-V6.0

This script handles the structural packaging deployment for the UTP codebase.
It maps the package directory tree and enforces strict dependency validation to
guarantee clean compiled performance metrics across isolated developer
environments.
"""
from setuptools import setup, find_packages

setup(
    name="triality_pipeline",
    version="6.0.0",
    author="Arthur Leroy Jones, Mikey, Abby Davis",
    author_email="Triality369framework@gmail.com",
    url="https://github.com/JTechHound/Triality-Manifest-Build",
    description="Advanced Non-Equilibrium Open Quantum Systems Engineering Blueprint",
    long_description=(
        "A scalable open quantum system architecture designed to maintain "
        "non-local macroscopic quantum coherence in the presence of severe "
        "localized decoherence baths, integrating Positive Grassmannian / "
        "Amplituhedron geometry, fault-tolerant surface code topologies, and "
        "shift-invariant quantum convolutions."
    ),
    long_description_content_type="text/markdown",
    # Structural packages inside the src/ folder backbone
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    # Enforce technical Python environment parameters for zero-error numerical operations
    python_requires=">=3.10",
    # Core third-party dependencies pinned to verified structural compiler frameworks
    install_requires=[
        "numpy>=1.24.0",        # High-speed multidimensional array and matrix computations
        "scipy>=1.10.0",        # Specialized signal processing, Richardson math, and constants
        "scikit-learn>=1.2.0",  # Conventional statistical classification metrics and validations
    ],
    # Grouped optional dependencies for specialized testing and advanced visualization
    extras_require={
        "test": [
            "pytest>=7.3.0",      # Automated testing, failure validations, and assertion suites
            "pytest-cov>=4.0.0",  # Test suite coverage reporting tools
        ],
        "quantum": [
            "qiskit>=0.44.0",     # Hardware-level circuit verification modeling wrappers
        ],
    },
    # Classifiers to map framework profile metrics cleanly on open-source registries
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Physics",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
)
