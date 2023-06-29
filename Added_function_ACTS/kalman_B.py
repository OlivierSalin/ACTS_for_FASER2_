#!/usr/bin/env python3

from pathlib import Path
from typing import Optional
import random

import acts
import acts.examples

u = acts.UnitConstants


def runTruthTrackingKalman(
    trackingGeometry: acts.TrackingGeometry,
    field: acts.MagneticFieldProvider,
    outputDir: Path,
    digiConfigFile: Path,
    directNavigation=False,
    reverseFilteringMomThreshold=0 * u.GeV,
    s: acts.examples.Sequencer = None,
    inputParticlePath: Optional[Path] = None,
):
    from acts.examples.simulation import (
        addParticleGun,
        EtaConfig,
        MomentumConfig,
        PhiConfig,
        ParticleConfig,
        addFatras,
        addDigitization,
    )
    from acts.examples.reconstruction import (
        addSeeding,
        SeedingAlgorithm,
        TruthSeedRanges,
        addKalmanTracks,
        addVertexFitting,
        VertexFinder,
    )

    s = s or acts.examples.Sequencer(
        events=50000, numThreads=-1, logLevel=acts.logging.INFO
    )

    rnd = acts.examples.RandomNumbers()
    outputDir = Path(outputDir)


    if inputParticlePath is None:
        addParticleGun(
            s,
            MomentumConfig(0 * u.GeV, 2500.0 * u.GeV),
            EtaConfig(-0.01, 0.01, uniform=True),
            PhiConfig(-0.06, 0.06 * u.degree),
            ParticleConfig(2, acts.PdgParticle.eMuon, True),
            vtxGen=acts.examples.GaussianVertexGenerator(
                stddev=acts.Vector4(
                    1300 * u.mm, 500 * u.mm, 200 * u.mm, 0 * u.ns
                ),
                mean=acts.Vector4(3750, 0, 0, 0),
            ),
            multiplicity=1,
            rnd=rnd,
            outputDirRoot=outputDir,
        )
        # addParticleGun(
        #     s,
        #     MomentumConfig(0 * u.GeV, 5000.0 * u.GeV),
        #     EtaConfig(4.0, 12.0, uniform=True),
        #     ParticleConfig(2, acts.PdgParticle.eMuon, True),
        #     vtxGen=acts.examples.GaussianVertexGenerator(
        #         stddev=acts.Vector4(
        #             200 * u.mm, 500 * u.mm, 1300 * u.mm, 0 * u.ns
        #         ),
        #         mean=acts.Vector4(0, 0, 3750, 0),
        #     ),
        #     multiplicity=1,
        #     rnd=rnd,
        #     outputDirRoot=outputDir,
        # )
    else:
        acts.logging.getLogger("Truth tracking example").info(
            "Reading particles from %s", inputParticlePath.resolve()
        )
        assert inputParticlePath.exists()
        s.addReader(
            acts.examples.RootParticleReader(
                level=acts.logging.INFO,
                filePath=str(inputParticlePath.resolve()),
                particleCollection="particles_input",
                orderedEvents=False,
            )
        )

    addFatras(
        s,
        trackingGeometry,
        field,
        rnd=rnd,
        # enableInteractions=True
    )

    addDigitization(
        s,
        trackingGeometry,
        field,
        digiConfigFile=digiConfigFile,
        rnd=rnd,
    )

    addSeeding(
        s,
        trackingGeometry,
        field,
        seedingAlgorithm=SeedingAlgorithm.TruthSmeared,
        rnd=rnd,
        truthSeedRanges=TruthSeedRanges(
            pt=(0 * u.MeV, None),
            nHits=(5, None),
            eta=(-0.5,0.5)
        ),
    )

    addKalmanTracks(
        s,
        trackingGeometry,
        field,
        directNavigation,
        reverseFilteringMomThreshold,
        energyLoss= True,
        multipleScattering= True,
    )

    addVertexFitting(
        s,
        field,
        vertexFinder=VertexFinder.Truth,
        outputDirRoot=outputDir,
    )



    # Output
    # s.addWriter(
    #     acts.examples.RootTrajectoryStatesWriter(
    #         level=acts.logging.INFO,
    #         inputTrajectories="trajectories",
    #         inputParticles="truth_seeds_selected",
    #         inputSimHits="simhits",
    #         inputMeasurementParticlesMap="measurement_particles_map",
    #         inputMeasurementSimHitsMap="measurement_simhits_map",
    #         filePath=str(outputDir / "trackstates_fitter.root"),
    #     )
    # )

    s.addWriter(
        acts.examples.RootTrajectorySummaryWriter(
            level=acts.logging.INFO,
            inputTrajectories="trajectories",
            inputParticles="truth_seeds_selected",
            inputMeasurementParticlesMap="measurement_particles_map",
            filePath=str(outputDir / "tracksummary_fitter.root"),
        )
    )

    s.addWriter(
        acts.examples.TrackFinderPerformanceWriter(
            level=acts.logging.INFO,
            inputProtoTracks="sorted_truth_particle_tracks"
            if directNavigation
            else "truth_particle_tracks",
            inputParticles="truth_seeds_selected",
            inputMeasurementParticlesMap="measurement_particles_map",
            filePath=str(outputDir / "performance_track_finder.root"),
        )
    )

    s.addWriter(
        acts.examples.TrackFitterPerformanceWriter(
            level=acts.logging.INFO,
            inputTrajectories="trajectories",
            inputParticles="truth_seeds_selected",
            inputMeasurementParticlesMap="measurement_particles_map",
            filePath=str(outputDir / "performance_track_fitter.root"),
        )
    )

    return s


if "__main__" == __name__:

    srcdir = Path(__file__).resolve().parent.parent.parent.parent

    detector, trackingGeometry, decorators = acts.examples.TelescopeDetector.create(
        bounds=[1000, 3000], positions=[10000,  10500, 11000, 19500, 20000,20500], binValue=0,thickness=4,
    )


    digiConfigFile= "/data/atlassmallfiles/users/salin/acts_F2/acts/Examples/Algorithms/Digitization/share/default-smearing-config-telescope.json"

    inputParticlePath = Path("/data/atlassmallfiles/users/salin/Acts_x/GEN/HepMC_Root/Root_DarkHiggs_X_good/Particles_DarkPhoton_m0.8128_mu_mu.root")
    if not inputParticlePath.exists():
        inputParticlePath = None

    B_value=[1.0, 0.75, 0.5]
    pos=[19500,24500,29500]

    field = acts.RestrictedBField(acts.Vector3(0* u.T, 0, 1.0 * u.T))
    #for B_field in B_value:
    #for posi_ in pos:
    masses=[0.2239,0.5012,0.8128,1.5849,3.5]
    resolution=[100,10,1]
    for res in resolution:
    #for mass_ in masses:
        rand_ = random.randint(0, 50000)
        #field = acts.RestrictedBField(acts.Vector3(0* u.T, 0, B_field* u.T))
        #field = acts.RestrictedBFieldCylindrical(acts.Vector3(0* u.T, 0, B_field * u.T))
    #     detector_misal, trackingGeometry_misal, decorators_misal = acts.examples.TelescopeDetector.create(
    #     bounds=[1000, 3000], positions=[10000,  10500, 11000, 19500, 20000,20500], binValue=0,thickness=4,
    # )
        # detector, trackingGeometry, decorators = acts.examples.TelescopeDetector.create(
        #     bounds=[1000, 3000], positions=[10000,  10500, 11000, posi_, posi_+500,posi_+1000], binValue=0,thickness=4,
        # )
        digiConfigFile= "/data/atlassmallfiles/users/salin/acts_F2/acts/Examples/Algorithms/Digitization/share/default-smearing-config-telescope.json"

        #inputParticlePath = Path(f"/data/atlassmallfiles/users/salin/Acts_x/GEN/HepMC_Root/Root_DarkHiggs_X_good/Particles_DarkPhoton_m{mass_}_mu_mu.root")
        inputParticlePath = Path(f"/data/atlassmallfiles/users/salin/Acts_x/GEN/HepMC_Root/Root_DarkHiggs_X_good/Particles_DarkPhoton_m0.8128_mu_mu.root")
        if not inputParticlePath.exists():
            inputParticlePath = None


        #outputDir = Path(f"./Output_ttk/HepMC_DarkPhoton_mu/DH_m0.8128/MisAlign/Test2/Kalman_SigInPlane_{sigmaInPlane_}_{rand_}")
        outputDir = Path(f"./Output_ttk/HepMC_DarkPhoton_mu/DH_m0.8128/Masses/Test2/Kalman_masse_{mass_}GeV")
        outputDir.mkdir(parents=True, exist_ok=True)

        runTruthTrackingKalman(
            trackingGeometry=trackingGeometry,
            #trackingGeometry_misal=trackingGeometry_misal,
            field=field,
            digiConfigFile=digiConfigFile,
            outputDir=outputDir,
            # outputDir="./Output_ttk/Out9",
            inputParticlePath=inputParticlePath,
        ).run()
