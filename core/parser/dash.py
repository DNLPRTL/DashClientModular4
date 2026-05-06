import xml.etree.ElementTree as ET
from core.parser.base import ParserBase
import struct
import math  # <-- añadido para el redondeo robusto

class DashParser(ParserBase):
    NAMESPACE = '{urn:mpeg:dash:schema:mpd:2011}'

    def __init__(self):
        super().__init__()
        self.mpd_root = None
        self.base_url = ""
        self.periods = []
        self._profiles = ""
        self.global_info = {}

    def load(self, manifest_path):
        if manifest_path.startswith("http"):
            import requests
            r = requests.get(manifest_path)
            r.raise_for_status()
            xml_content = r.content
            tree = ET.ElementTree(ET.fromstring(xml_content))
        else:
            tree = ET.parse(manifest_path)

        self.mpd_root = tree.getroot()
        mpd = self.mpd_root

        # ----- Info global -----
        self.global_info = {
            'minBufferTime': mpd.attrib.get('minBufferTime', ''),
            'type': mpd.attrib.get('type', ''),
            'mediaPresentationDuration': mpd.attrib.get('mediaPresentationDuration', ''),
            'maxSegmentDuration': mpd.attrib.get('maxSegmentDuration', ''),
            'profiles': mpd.attrib.get('profiles', ''),
            'availabilityStartTime': mpd.attrib.get('availabilityStartTime', ''),
            'publishTime': mpd.attrib.get('publishTime', ''),
        }

        proginfo = mpd.find(f'{self.NAMESPACE}ProgramInformation')
        if proginfo is not None:
            self.global_info['programInformation'] = {
                'moreInformationURL': proginfo.attrib.get('moreInformationURL', ''),
                'title': '',
            }
            title = proginfo.find(f'{self.NAMESPACE}Title')
            if title is not None and title.text:
                self.global_info['programInformation']['title'] = title.text.strip()
        else:
            self.global_info['programInformation'] = {}

        base_url_elem = mpd.find(f'{self.NAMESPACE}BaseURL')
        if base_url_elem is not None and base_url_elem.text:
            self.base_url = base_url_elem.text.strip()
        elif manifest_path.startswith("http"):
            import urllib.parse
            self.base_url = urllib.parse.urljoin(manifest_path, './')
        else:
            self.base_url = "/".join(manifest_path.split("/")[:-1]) + "/"

        self._profiles = mpd.attrib.get('profiles', '')

        # ----- Periods -----
        self.periods = []
        for period in mpd.findall(f'{self.NAMESPACE}Period'):
            period_data = {
                'id': period.attrib.get('id', ''),
                'start': period.attrib.get('start', ''),
                'duration': period.attrib.get('duration', ''),
                'adaptationSets': []
            }
            period_duration = period.attrib.get('duration', '') or self.global_info['mediaPresentationDuration']
            period_seconds = self.parse_duration(period_duration)

            for adap in period.findall(f'{self.NAMESPACE}AdaptationSet'):
                adap_type = adap.attrib.get('contentType', '')
                lang = adap.attrib.get('lang', '')
                mime = adap.attrib.get('mimeType', '')
                reps = []

                for idx, rep in enumerate(adap.findall(f'{self.NAMESPACE}Representation')):
                    rep_id = rep.attrib.get('id', str(idx))
                    rep_mime = rep.attrib.get('mimeType', mime)
                    bw = int(rep.attrib.get('bandwidth', 0))
                    width = int(rep.attrib.get('width', 0))
                    height = int(rep.attrib.get('height', 0))
                    codecs = rep.attrib.get('codecs', '')
                    frame_rate = rep.attrib.get('frameRate', '')
                    sar = rep.attrib.get('sar', '')
                    audio_sampling_rate = rep.attrib.get('audioSamplingRate', '')
                    start_with_sap = rep.attrib.get('startWithSAP', '')
                    audio_channels = ''
                    audio_config = rep.find(f'{self.NAMESPACE}AudioChannelConfiguration')
                    if audio_config is not None:
                        audio_channels = audio_config.attrib.get('value', '')

                    baseurl_elem = rep.find(f'{self.NAMESPACE}BaseURL')
                    media_url = ""
                    if baseurl_elem is not None and baseurl_elem.text:
                        media_url = self.abs_url(baseurl_elem.text.strip())
                    else:
                        media_url = self.base_url

                    segments = []
                    init_url = ""
                    segment_base_info = None
                    fragment_duration = None
                    segment_durations = None
                    byte_ranges = None

                    # --- SegmentList ---
                    seg_list = rep.find(f'{self.NAMESPACE}SegmentList')
                    if seg_list is not None:
                        timescale = int(seg_list.attrib.get('timescale', '1'))
                        duration = int(seg_list.attrib.get('duration', '0'))
                        if duration > 0:
                            fragment_duration = duration / timescale
                        init_elem = seg_list.find(f'{self.NAMESPACE}Initialization')
                        if init_elem is not None:
                            init_url = self.abs_url(init_elem.attrib.get('sourceURL', ''))
                        for seg_url in seg_list.findall(f'{self.NAMESPACE}SegmentURL'):
                            url = self.abs_url(seg_url.attrib.get('media', ''))
                            segments.append(url)
                        if fragment_duration is None and len(segments) > 0:
                            fragment_duration = period_seconds / len(segments)

                        # ---- Duraciones: residual CAPADO al fragment_duration ----
                        segment_durations = []
                        if fragment_duration is not None and len(segments) > 0:
                            n = len(segments)
                            if n == 1:
                                segment_durations = [period_seconds or fragment_duration]
                            else:
                                for i in range(n - 1):
                                    segment_durations.append(fragment_duration)
                                residual = max(0.0, period_seconds - fragment_duration * (n - 1))
                                # FIX: no inflar el último más que la duración nominal
                                last = min(fragment_duration, residual)
                                segment_durations.append(last)

                    else:
                        # --- SegmentTemplate ---
                        seg_template = rep.find(f'{self.NAMESPACE}SegmentTemplate')
                        if seg_template is None:
                            seg_template = adap.find(f'{self.NAMESPACE}SegmentTemplate')
                        if seg_template is not None:
                            timescale = int(seg_template.attrib.get('timescale', '1'))
                            duration = int(seg_template.attrib.get('duration', '0'))
                            if duration > 0:
                                fragment_duration = duration / timescale
                            init_attr = seg_template.attrib.get('initialization', '')
                            if init_attr:
                                url_init = self.resolve_template(init_attr, rep_id=rep_id, bandwidth=bw)
                                init_url = self.abs_url(url_init)
                            media_tpl = seg_template.attrib.get('media', '')
                            start_num = int(seg_template.attrib.get('startNumber', '1'))

                            # === Ajuste: cálculo robusto del nº de segmentos ===
                            if duration > 0:
                                ratio = (period_seconds * timescale) / duration
                                n_segments = int(round(ratio))
                            else:
                                n_segments = 30

                            for n in range(start_num, start_num + n_segments):
                                seg_url = self.resolve_template(media_tpl, rep_id=rep_id, number=n, bandwidth=bw)
                                segments.append(self.abs_url(seg_url))
                            if fragment_duration is None and n_segments > 0:
                                fragment_duration = period_seconds / n_segments

                            # Duraciones con residual CAPADO
                            segment_durations = []
                            if fragment_duration is not None and len(segments) > 0:
                                n = len(segments)
                                if n == 1:
                                    segment_durations = [period_seconds or fragment_duration]
                                else:
                                    for i in range(n - 1):
                                        segment_durations.append(fragment_duration)
                                    residual = max(0.0, period_seconds - fragment_duration * (n - 1))
                                    last = min(fragment_duration, residual)
                                    segment_durations.append(last)

                        else:
                            # --- SegmentBase (OnDemand) + SIDX ---
                            seg_base = rep.find(f'{self.NAMESPACE}SegmentBase')
                            if seg_base is not None and media_url:
                                init_elem = seg_base.find(f'{self.NAMESPACE}Initialization')
                                init_range = init_elem.attrib.get('range', '') if init_elem is not None else ''
                                index_range = seg_base.attrib.get('indexRange', '')
                                segment_base_info = {
                                    'media_url': media_url,
                                    'init_range': init_range,
                                    'index_range': index_range,
                                }
                                init_url = media_url
                                segment_durations = []
                                byte_ranges = []
                                segments = []
                                if index_range:
                                    try:
                                        range_start, range_end = map(int, index_range.split('-'))
                                        # leer SIDX
                                        if media_url.startswith("http"):
                                            import requests
                                            headers = {"Range": f"bytes={range_start}-{range_end}"}
                                            resp = requests.get(media_url, headers=headers)
                                            sidx_data = resp.content
                                        else:
                                            with open(media_url, "rb") as f:
                                                f.seek(range_start)
                                                sidx_data = f.read(range_end - range_start + 1)
                                        timescale, durations = self._parse_sidx(sidx_data)
                                        # TRUST SIDX: no ajustar al period_seconds
                                        segment_durations = [d['duration'] / float(timescale) for d in durations]
                                        fragment_duration = segment_durations[0] if segment_durations else period_seconds
                                        # construir byte ranges reales
                                        seg_ranges = []
                                        byte_offset = range_end + 1
                                        for d in durations:
                                            start = byte_offset
                                            end = start + d['size'] - 1
                                            seg_ranges.append(f"{start}-{end}")
                                            byte_offset = end + 1
                                        segments = [media_url] * len(seg_ranges)
                                        byte_ranges = seg_ranges
                                    except Exception as e:
                                        print("⚠️  Error leyendo SIDX en", media_url, ":", e)
                                        # fallback seguro
                                        segment_durations = [period_seconds]
                                        fragment_duration = period_seconds
                                        segments = [media_url]
                                        byte_ranges = [None]
                                else:
                                    segment_durations = [period_seconds]
                                    fragment_duration = period_seconds
                                    segments = [media_url]
                                    byte_ranges = [None]

                    # Fallback: si aún no hay fragment_duration pero sí varios segmentos
                    if fragment_duration is None and len(segments) > 1:
                        fragment_duration = period_seconds / len(segments)

                    rep_info = {
                        'id': rep_id,
                        'mimeType': rep_mime,
                        'bandwidth': bw,
                        'width': width,
                        'height': height,
                        'codecs': codecs,
                        'frameRate': frame_rate,
                        'sar': sar,
                        'audioSamplingRate': audio_sampling_rate,
                        'audioChannels': audio_channels,
                        'startWithSAP': start_with_sap,
                        'lang': lang,
                        'adaptationType': adap_type,
                        'init_url': init_url,
                        'segments': segments,
                        'fragment_duration': fragment_duration if fragment_duration is not None else 1.0,
                        'segment_durations': segment_durations,
                        'byte_ranges': byte_ranges,
                    }
                    if segment_base_info is not None:
                        rep_info['segment_base_info'] = segment_base_info
                    reps.append(rep_info)

                period_data['adaptationSets'].append({
                    'type': adap_type,
                    'lang': lang,
                    'mimeType': mime,
                    'representations': reps
                })
            self.periods.append(period_data)

    def resolve_template(self, tpl, rep_id=None, number=None, bandwidth=None):
        url = tpl
        if '$RepresentationID$' in url and rep_id is not None:
            url = url.replace('$RepresentationID$', str(rep_id))
        if '$Number$' in url and number is not None:
            url = url.replace('$Number$', str(number))
        if '$Bandwidth$' in url and bandwidth is not None:
            url = url.replace('$Bandwidth$', str(bandwidth))
        return url

    def abs_url(self, url):
        if url.startswith("http"):
            return url
        return self.base_url + url

    @staticmethod
    def parse_duration(duration_str):
        import re
        if not duration_str:
            return 0
        match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?([\d\.]+)S', duration_str)
        hours = int(match.group(1)) if match and match.group(1) else 0
        minutes = int(match.group(2)) if match and match.group(2) else 0
        seconds = float(match.group(3)) if match and match.group(3) else 0.0
        return hours * 3600 + minutes * 60 + seconds

    @staticmethod
    def _parse_sidx(data):
        # Minimal SIDX parser
        offset = 0
        size = struct.unpack(">I", data[offset:offset+4])[0]
        box_type = data[offset+4:offset+8]
        if box_type != b'sidx':
            return None, []
        offset += 8
        version = data[offset]
        offset += 4  # version+flags
        _ = struct.unpack(">I", data[offset:offset+4])[0]  # reference_ID
        offset += 4
        timescale = struct.unpack(">I", data[offset:offset+4])[0]
        offset += 4
        if version == 0:
            offset += 4  # earliest_presentation_time
            offset += 4  # first_offset
        else:
            offset += 8
            offset += 8
        offset += 2  # reserved
        ref_count = struct.unpack(">H", data[offset:offset+2])[0]
        offset += 2

        durations = []
        for _i in range(ref_count):
            ref_info = struct.unpack(">I", data[offset:offset+4])[0]
            ref_type = (ref_info >> 31) & 0x1
            ref_size = ref_info & 0x7FFFFFFF
            offset += 4
            subsegment_duration = struct.unpack(">I", data[offset:offset+4])[0]
            offset += 4
            offset += 4  # SAP
            durations.append({'size': ref_size, 'duration': subsegment_duration})

        return timescale, durations

    def get_mpd_info(self):
        return self.global_info

    def get_periods(self):
        return self.periods
