# coding=utf-8
from mezzanine.pages.page_processors import processor_for
from portal.ferramentas.forms import SSLCheckerForm, CSRDecoderForm, CertificateKeyMatcherForm, SSLConverterForm, CSRDecodeError
from portal.ferramentas.models import FerramentasPage


@processor_for(FerramentasPage)
def ferramentas_processor(request, page):

    ssl_checker_form = SSLCheckerForm()
    csr_decoder_form = CSRDecoderForm()
    certificated_key_matcher_form = CertificateKeyMatcherForm()
    ssl_converter_form = SSLConverterForm()
    resultado = ''

    if request.method == 'POST':
        op = request.POST.get('operation')
        if op == 'ssl-checker':
            ssl_checker_form = SSLCheckerForm(request.POST)
            if ssl_checker_form.is_valid():
                resultado = ssl_checker_form.processa()
        elif op == 'csr-decoder':
            csr_decoder_form = CSRDecoderForm(request.POST)
            if csr_decoder_form.is_valid():
                try:
                    resultado = csr_decoder_form.processa()
                except:
                    resultado = {
                        'ok': False
                    }

        elif op == 'certificate-key-matcher':
            certificated_key_matcher_form = CertificateKeyMatcherForm(request.POST, request.FILES)
            if certificated_key_matcher_form.is_valid():
                try:
                    resultado = certificated_key_matcher_form.processa()
                except Exception as e:
                    print e
                    resultado = {
                        'ok': False
                    }
        elif op == 'ssl-converter':
            ssl_converter_form = SSLConverterForm(request.POST),
    else:
        op = ''

    return {
        'op': op,
        'resultado': resultado,
        'form_ssl_checker': ssl_checker_form,
        'form_csr_decoder': csr_decoder_form,
        'form_certificated_key_matcher': certificated_key_matcher_form,
        'form_ssl_converter': ssl_converter_form,
    }