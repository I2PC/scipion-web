/***************************************************************************
 *
 * Authors:     Carlos Oscar S. Sorzano (coss@cnb.csic.es)
 *
 * Unidad de  Bioinformatica of Centro Nacional de Biotecnologia , CSIC
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
 * 02111-1307  USA
 *
 *  All comments concerning this program package may be sent to the
 *  e-mail address 'xmipp@cnb.csic.es'
 ***************************************************************************/

#include "phantom_simulate_microscope.h"

#include <data/args.h>

/* Read parameters --------------------------------------------------------- */
void ProgSimulateMicroscope::readParams()
{
    XmippMetadataProgram::readParams();

    fn_ctf = "";//initialize empty, force recalculation of first time
    if (checkParam("--ctf"))
    {
        //Fill the input metadata with the value of 'fn_ctf'
        MDConstGenerator generator(getParam("--ctf"));
        generator.label = MDL_CTFMODEL;
        generator.fill(mdIn);
    }
    else
    {
        if (mdIn.containsLabel(MDL_CTFMODEL))
        {
            //sort the images according to the ctf to avoid the recaculation of it
            //beeten images of the same ctf group
            MetaData md(mdIn);
            mdIn.sort(md, MDL_CTFMODEL);
        }
        else
            REPORT_ERROR(ERR_ARG_MISSING, "You should provide param --ctf or it should be present on input metadata");
    }
    sigma = getDoubleParam("--noise");
    low_pass_before_CTF = getDoubleParam("--low_pass");
    after_ctf_noise = checkParam("--after_ctf_noise");
    defocus_change = getDoubleParam("--defocus_change");
}

/* Usage ------------------------------------------------------------------- */
void ProgSimulateMicroscope::defineParams()
{
    each_image_produces_an_output = true;
    save_metadata_stack = true;
    XmippMetadataProgram::defineParams();

    addUsageLine("Simulate the effect of the microscope on ideal projections.");
    addExampleLine("Example of use: Generate a set of images with the CTF applied without any noise", false);
    addExampleLine("   xmipp_phantom_simulate_microscope -i g0ta.sel --oroot g1ta --ctf untilt_ARMAavg.ctfparam");
    addExampleLine("Example of use: Generate a set of images with the CTF applied and noise before and after CTF", false);
    addExampleLine("   xmipp_phantom_simulate_microscope -i g0ta.sel --oroot g2ta --ctf untilt_ARMAavg.ctfparam --noise 4.15773 --after_ctf_noise");

    addParamsLine(" [--ctf <CTFdescr>]       : a CTF description, if this param is not supplied it should come in metadata");
    addParamsLine(" [--after_ctf_noise]      : apply noise after CTF");
    addParamsLine(" [--defocus_change <v=0>] : change in the defocus value (percentage)");
    addParamsLine(" [--low_pass <w=0>]       : low pass filter for noise before CTF");
    addParamsLine(" [--noise <stddev=0>]     : noise to be added");



}

/* Show -------------------------------------------------------------------- */
void ProgSimulateMicroscope::show()
{
    XmippMetadataProgram::show();
    if (verbose)
        std::cout << "CTF file: " << fn_ctf << std::endl
        << "Noise: " << sigma << std::endl
        << "Noise before: " << sigma_before_CTF << std::endl
        << "Noise after: " << sigma_after_CTF << std::endl
        << "Low pass freq: " << low_pass_before_CTF << std::endl
        << "After CTF noise: " << after_ctf_noise << std::endl
        << "Defocus change: " << defocus_change << std::endl
        ;
}

void ProgSimulateMicroscope::setupFourierFilter(ProgFourierFilter &filter, bool isBackground, double &power)
{
    static int dXdim = 2 * Xdim, dYdim = 2 * Ydim;
    static MultidimArray<double> aux;

    filter.FilterBand = CTF;
    filter.ctf.read(fn_ctf);
    filter.ctf.enable_CTF = !isBackground;
    filter.ctf.enable_CTFnoise = isBackground;
    filter.ctf.Produce_Side_Info();
    aux.resize(dYdim, dXdim);
    aux.setXmippOrigin();
    //filter.do_generate_3dmask=true;
    filter.do_generate_3dmask = isBackground;
    filter.generateMask(aux);
    power = filter.maskPower();
}

void ProgSimulateMicroscope::updateCtfs()
{
    double before_power = 0, after_power = 0;
    sigma_after_CTF = sigma_before_CTF = 0;

    setupFourierFilter(ctf, false, before_power);

    if (after_ctf_noise)
        setupFourierFilter(after_ctf, true, after_power);

    // Compute noise balance
    if (after_power != 0 || before_power != 0)
    {
        double p = after_power / (after_power + before_power);
        double K = 1 / sqrt(p * after_power + (1 - p) * before_power);
        sigma_after_CTF = sqrt(p) * K * sigma;
        sigma_before_CTF = sqrt(1 - p) * K * sigma;
    }
    else if (sigma != 0)
    {
        sigma_before_CTF = sigma;
        sigma_after_CTF = 0;
    }
}

/* Produce side information ------------------------------------------------ */
void ProgSimulateMicroscope::preProcess()
{
    int dum;
    size_t dum2;

    //if (command_line) get_input_size(Zdim, Ydim, Xdim);
    ImgSize(mdIn, Xdim, Ydim, dum, dum2);

    if (low_pass_before_CTF != 0)
    {
        lowpass.FilterBand = LOWPASS;
        lowpass.FilterShape = RAISED_COSINE;
        lowpass.w1 = low_pass_before_CTF;
    }
}

void ProgSimulateMicroscope::processImage(const FileName &fnImg, const FileName &fnImgOut, size_t objId)
{
    static Image<double> img;
    static FileName last_ctf;
    last_ctf = fn_ctf;
    img.readApplyGeo(fnImg, mdIn, objId);

    mdIn.getValue(MDL_CTFMODEL, fn_ctf, objId);
    if (fn_ctf != last_ctf)
        updateCtfs();

    if (ZSIZE(img())!=1)
        REPORT_ERROR(ERR_MULTIDIM_DIM,"This process is not intended for volumes");

    apply(img());

    img.write(fnImgOut);
}


/* Apply ------------------------------------------------------------------- */
void ProgSimulateMicroscope::apply(MultidimArray<double> &I)
{
    I.setXmippOrigin();
    I.selfWindow(FIRST_XMIPP_INDEX(2*Ydim), FIRST_XMIPP_INDEX(2*Xdim),
                 LAST_XMIPP_INDEX(2*Ydim), LAST_XMIPP_INDEX(2*Xdim));

    // Add noise before CTF
    MultidimArray<double> noisy;
    noisy.resize(I);
    noisy.initRandom(0, sigma_before_CTF, "gaussian");
    if (low_pass_before_CTF != 0)
        lowpass.applyMaskSpace(noisy);
    I += noisy;

    // Check if the mask is a defocus changing CTF
    // In that case generate a new mask with a random defocus
    if (defocus_change != 0)
    {
        double old_DefocusU = ctf.ctf.DeltafU;
        double old_DefocusV = ctf.ctf.DeltafV;
        MultidimArray<double> aux;
        ctf.ctf.DeltafU *= rnd_unif(1 - defocus_change / 100, 1 + defocus_change / 100);
        ctf.ctf.DeltafV *= rnd_unif(1 - defocus_change / 100, 1 + defocus_change / 100);
        aux.initZeros(2*Ydim, 2*Xdim);
        ctf.generateMask(aux);
        ctf.ctf.DeltafU = ctf.ctf.DeltafU;
        ctf.ctf.DeltafV = ctf.ctf.DeltafV;
    }

    // Apply CTF
    ctf.applyMaskSpace(I);

    // Add noise after CTF
    noisy.initRandom(0, sigma_after_CTF, "gaussian");
    if (after_ctf_noise)
        after_ctf.applyMaskSpace(noisy);
    I += noisy;
    I.selfWindow(FIRST_XMIPP_INDEX(Ydim), FIRST_XMIPP_INDEX(Xdim),
                 LAST_XMIPP_INDEX(Ydim), LAST_XMIPP_INDEX(Xdim));
}

