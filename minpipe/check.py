from subprocess import run
from pathlib import Path
import logging

class TestSamples():
    def __init__(self, logger, single, complement, samples, format) -> None:
        self.samples = samples
        self.complement = complement
        self.single = single
        self.logger = logger
        pass

    def read_samples(self) -> None:
        if self.single and self.complement is not None:
            self.logger.info("Single-ended analysis does not contain complements. \
                Complements are for paired-ended (e.g. sample1_R1.fastq.gz and sample1_R2.fastq.gz)")
            exit()
        elif not self.single and self.complement is not None:
            if len(self.complement) > 2:
                self.logger.info("Complement (-c or --complement) argument has to be maximum \
                    of 2 for paired-ended reads.")
                exit()

        if not self.single:
            for file in self.samples:
                if Path(f"input/{file}{self.complement[0]}{self.format}").is_file() \
                        and Path(f"input/{file}{self.complement[1]}{self.format}").is_file():
                    pass
                else:
                    self.logger.info(f"File {file} does not exist in input/ folder.")
                    exit()
        elif self.single:
            for file in self.samples:
                if Path(f"input/{file}{self.format}").is_file():
                    pass
                else:
                    self.logger.info(f"File {file} does not exist in input/ folder.")
                    exit()

        self.logger.info("All files exists. Continuing the analysis.")

        pass

    def __exit__(self, type, value, traceback):
        try:
            run(args=[], text=True, capture_output=True)
        except Exception as exc:
            print(exc)

class TestIndexTranscript():
    def __init__(self, logger, transcript, index) -> None:
        self.logger = logger
        self.transcript = transcript
        self.index = index
        pass

    def __download_hsa_transcript(self) -> None:
        try:
            run([
                "wget", "-P", "index/", "-c",
                "http://ftp.ensembl.org/pub/release-104/fasta/homo_sapiens/cdna/Homo_sapiens.GRCh38.cdna.all.fa.gz",
                "-O", "index/homo_sapiens_GRCh38_cdna.fa.gz"
            ])
        except Exception as exc:
            self.logger.info(exc)
            quit()

        self.logger.info("Homo sapiens transcript has been downloaded!")
        self.transcript = ["homo_sapiens_GRCh38_cdna.fa.gz"]
        
        pass


    def __download_mmu_trscript(self) -> None:
        try:
            run([
                "wget", "-P", "index/", "-c",
                "http://ftp.ensembl.org/pub/release-104/fasta/mus_musculus/cdna/Mus_musculus.GRCm39.cdna.all.fa.gz",
                "-O", "index/mus_musculus_GRCm39_cdna.fa.gz"
            ])
        except Exception as exc:
            self.logger.info(exc)
            quit()

        self.logger.info("Mus musculus transcript has been downloaded!")
        self.transcript = ["mus_musculus_GRCm39_cdna.fa.gz"]
        
        pass

    def __check_index(path_index: str):
        if Path(path_index).is_file():
            pass
        else:
            exit(f"No index file found on {path_index}")

        pass

    def create_index(self) -> None:
        if "/" in self.transcript[0]:
            idx_name = self.transcript[0].split("/")[-1].split(".")[0]
        else:
            idx_name = self.transcript[0].split(".")[0]

        idx = run(["kallisto", "index", "-i", f"index/{idx_name}.idx",
                f"index/{self.transcript[0]}"], capture_output=True, text=True)
        self.logger.info(idx.stdout)
        self.logger.info(idx.stderr)

        self.index = [f"index/{idx_name}.idx"]

        pass

    def check_idx_trans(self) -> None:
        if self.index is None and self.transcript is None:
            self.logger.info("No index or transcript has been passed")
            exit()
        elif self.index is None and self.transcript:
            if any(fmt in self.transcript[0] for fmt in ['.fa', '.fa.gz',
                                                        '.fastq', '.fastq.gz',
                                                        '.fq', '.fq.gz']):
                try:
                    self.create_index(self)
                    self.logger.info("Index created")
                    self.__check_index(self.index)
                except Exception as ex:
                    self.logger.info(ex)
                    exit()
            else:
                if self.transcript[0].lower() == "mmu":
                    self.__download_mmu_trscript(self)
                    self.create_index(self)
                    self.logger.info("Mmu transcript downloaded and index created.")
                    self.__check_index(self.index)
                elif self.transcript[0].lower() == "hsa":
                    self.__download_hsa_transcript(self)
                    self.create_index(self)
                    self.logger.info("Hsa transcript downloaded and index created.")
                    self.__check_index(self.index)
                else:
                    self.logger.info("Species or format not supported. \
                        Select hsa or mmu, or download your own transcript.")
                    exit()
        elif self.index and self.transcript is None:
            try:
                self.__check_index("index/" + self.index[0])
            except Exception as ex:
                self.logger.info(ex)
                exit()
        else:
            self.logger.info("You can only pass `--index` or `--transcript` argument. \
                If both are passed the pipeline don't know if needs to build another index with \
                    the transcript passed or use the index without building a new one.")
            exit()

        pass