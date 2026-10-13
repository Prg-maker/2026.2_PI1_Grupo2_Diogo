import { FaCheck } from "react-icons/fa6";
import { VscErrorCompact } from "react-icons/vsc";
import { IoMdClock } from "react-icons/io";


export function RelatorioPage() {
    return(
        <main className="flex-1 overflow-y-auto px-4 pb-4 pt-34 text-slate-200 sm:p-12">


            <header className="">
                <h1 className="text-2xl font-semibold text-slate-100">Relatórios</h1>
                <span className="text-sm text-slate-400">
                    Geração de relatórios em PDF por execução
                </span>
            </header>
            
            <div  className="w-full h-full mt-5 flex  gap-[20px]">

                
                <div className="h-[600px] w-[700px]  bg-[#0B1628] border border-[#1D293D]/60 rounded-[12px] px-[10px] pt-3 flex flex-col gap-2" >
                    <p > Selecionar Execução</p>

                    <a className="hover:bg-[#00B8DB]/10 border border-transparent hover:border-[#00B8DB]/20 transition cursor-pointer  rounded-lg gap-2 p-2 justify-between flex ">
                        <div className="flex flex-row gap-3">
                            <div className="w-2 h-2 bg-[#00D492] rounded-full mt-1"/>
                            <div className="text-[12px] flex flex-col gap-1 " >
                                <span className="">#0014</span>
                                <span>Labirinto · Flood Fill v2</span>
                                <span>15 de set 2025</span>
                            </div>

                        </div>

                        <FaCheck className="w-3 h-3 text-[#00D492] "/>
                    </a>


                    <a  className="hover:bg-[#00B8DB]/10 border border-transparent hover:border-[#00B8DB]/20 transition cursor-pointer  rounded-lg gap-2 p-2 justify-between flex ">
                        <div className="flex flex-row gap-3">
                            <div className="w-2 h-2 bg-[#FF6467] rounded-full mt-1"/>
                            <div className="text-[12px] flex flex-col gap-1 " >
                                <span className="">#0014</span>
                                <span>Labirinto · Flood Fill v2</span>
                                <span>15 de set 2025</span>
                            </div>

                        </div>

                        <VscErrorCompact className="w-3 h-3 text-[#FF6467] "/>
                    </a>



                </div>

               <div className="w-full flex flex-col gap-4    ">

                 <div className="h-[390px] w-full bg-[#0B1628] h-[500px] border border-[#1D293D]/60 rounded-[12px] p-4" >
                    
                    
                    <div className="flex justify-between">
                        <div>
                            <p className="text-[14px]">Execução #0014</p>
                            <span className="text-[#62748E] text-[12px]" >Labirinto · 18 set 2026</span>
                        </div>
                        
                        <p className="text-[#00D492] text-[14px]">Sucesso</p>


                    </div>



                <div className="grid grid-rows-2 grid-cols-3 gap-4 mt-4 ">

                    <div className="flex flex-col justify-center bg-[#0F172B] rounded-[8px] w-full  h-[92px] ">


                        <IoMdClock className="w-5 h-5"/>

                       
                        <p>03:42</p>
                        <span className="text-[12px] text-[#62748E]  ">min/s</span>
                        <span className="text-[12px] text-[#62748E]  ">Tempo total</span>
                    </div>


                    <div className="flex flex-col bg-[#0F172B] p-4 rounded-[8px]">


                        <IoMdClock className="w-5 h-5"/>

                       
                        <p>03:42</p>
                        <span className="text-[12px] text-[#62748E]  ">min/s</span>
                        <span className="text-[12px] text-[#62748E]  ">Tempo total</span>
                    </div>

                    <div className="flex flex-col bg-[#0F172B] p-4 rounded-[8px]">


                        <IoMdClock className="w-5 h-5"/>

                       
                        <p>03:42</p>
                        <span className="text-[12px] text-[#62748E]  ">min/s</span>
                        <span className="text-[12px] text-[#62748E]  ">Tempo total</span>
                    </div>



                    <div className="flex flex-col bg-[#0F172B] p-4 rounded-[8px]">


                        <IoMdClock className="w-5 h-5"/>

                       
                        <p>03:42</p>
                        <span className="text-[12px] text-[#62748E]  ">min/s</span>
                        <span className="text-[12px] text-[#62748E]  ">Tempo total</span>
                    </div>



                    <div className="flex flex-col bg-[#0F172B] p-4 rounded-[8px]">


                        <IoMdClock className="w-5 h-5"/>

                       
                        <p>03:42</p>
                        <span className="text-[12px] text-[#62748E]  ">min/s</span>
                        <span className="text-[12px] text-[#62748E]  ">Tempo total</span>
                    </div>


                    <div className="flex flex-col bg-[#0F172B] p-4 rounded-[8px]">


                        <IoMdClock className="w-5 h-5"/>

                       
                        <p>03:42</p>
                        <span className="text-[12px] text-[#62748E]  ">min/s</span>
                        <span className="text-[12px] text-[#62748E]  ">Tempo total</span>
                    </div>

                    <div>
                        <p className="text-[#62748E] text-[12px] uppercase">Conteúdo do Relatório</p>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                  {[
                    'Resumo executivo',
                    'Mapa do labirinto explorado',
                    'Gráficos de telemetria',
                    'Log de eventos',
                    'Análise de algoritmo',
                    'Comparativo com execuções anteriores',
                  ].map((item) => (
                    <div key={item} className="flex items-center gap-2 text-xs text-slate-400">
                      <svg viewBox="0 0 24 24" fill="none" stroke="#10b981" strokeWidth={2.5} className="w-3.5 h-3.5 flex-shrink-0">
                        <path d="M5 13l4 4L19 7" strokeLinecap="round" strokeLinejoin="round" />
                      </svg>
                      {item}
                    </div>
                  ))}
                </div>
                    </div>
                    
                </div>

                    


                </div>

                <div className="h-[126px] w-full bg-[#0B1628] border border-[#1D293D]/60 rounded-[12px]" >
                    a
                </div>
               </div>

                
            </div>

        </main>
    )
}